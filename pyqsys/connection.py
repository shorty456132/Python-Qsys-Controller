import json
import socket
import threading
import time
from typing import Optional, Callable, Dict, Any
from .exceptions import ConnectionError, ProtocolError


class QSYSConnection:
    """Handles the TCP socket connection to Q-SYS Core"""
    
    def __init__(self, host: str, port: int = 1710):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.Lock()
        self._callbacks: Dict[int, Callable] = {}
        self._message_id = 0
        self._last_communication = 0.0  # Track last communication time
        self._keep_alive_thread = None
        
    def _start_keep_alive(self):
        """Starts the keep-alive thread that sends NoOp commands"""
        def keep_alive():
            while self._connected:
                current_time = time.time()
                # If no communication for 45 seconds, send NoOp (well before 60-second timeout)
                if current_time - self._last_communication > 45:
                    self.send_command("NoOp", {})
                time.sleep(5)  # Check every 5 seconds
                
        self._keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        self._keep_alive_thread.start()

    def connect(self) -> None:
        """Establishes connection to Q-SYS Core"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self._connected = True
            # Start listener thread
            self._listener_thread = threading.Thread(target=self._listen, daemon=True)
            self._listener_thread.start()
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to Q-SYS Core: {e}")

    def disconnect(self) -> None:
        """Closes the connection to Q-SYS Core"""
        if self.socket:
            self._connected = False
            self.socket.close()
            self.socket = None

    def send_command(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None) -> int:
        """Sends a command to Q-SYS Core"""
        if not self._connected:
            raise ConnectionError("Not connected to Q-SYS Core")

        with self._lock:
            # Use incrementing IDs for commands, but fixed ID for change group
            if "ChangeGroup" in method:
                message_id = 1234
            else:
                self._message_id += 1
                message_id = self._message_id

            message = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": message_id
            }

            if callback:
                self._callbacks[message_id] = callback

            try:
                # Add null terminator as required by QRC protocol
                print(f"Sending: {message}")
                message_bytes = json.dumps(message).encode() + b'\0'
                self.socket.sendall(message_bytes)
                return message_id
            except socket.error as e:
                raise ProtocolError(f"Failed to send command: {e}")

    def _listen(self) -> None:
        """Listens for responses from Q-SYS Core"""
        buffer = ""
        while self._connected:
            try:
                data = self.socket.recv(4096).decode()
                if not data:
                    continue

                buffer += data
                while '\0' in buffer:
                    message, buffer = buffer.split('\0', 1)
                    self._handle_message(json.loads(message))

            except socket.error as e:
                if self._connected:  # Only raise if we're supposed to be connected
                    raise ConnectionError(f"Connection lost: {e}")

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handles incoming messages from Q-SYS Core"""
        print(f"Received message: {message}")
        
        # Check if this is a change group update (it won't have an 'id' field)
        if 'method' in message and message.get('method') == 'ChangeGroup.AutoPoll':
            print(f"Change Group Update: {message.get('params', {})}")
            return
    
        # Handle normal command responses
        message_id = message.get('id')
        if message_id in self._callbacks:
            callback = self._callbacks.pop(message_id)
            callback(message)
