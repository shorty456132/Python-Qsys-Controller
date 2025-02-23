from typing import Optional, Dict, Any, List
from .connection import QSYSConnection
from .models.change_group import ChangeGroup
from .models.response import QSYSResponse
from .exceptions import AuthenticationError
from .exceptions import QSYSError
import threading

class QSYSClient:
    """High-level client for interacting with Q-SYS Core"""
    
    MAX_CHANGE_GROUPS = 4  # Q-SYS has a limit of 4 change groups
    
    def __init__(self, host: str, port: int = 1710, redundant_host: Optional[str] = None):
        self.connection = QSYSConnection(host, port)
        self.redundant_connection = QSYSConnection(redundant_host, port) if redundant_host else None
        self.change_groups: Dict[str, ChangeGroup] = {}
        self.active_core = None  # Track which core is active

    def connect(self) -> None:
        """Establishes connection to Q-SYS Core"""
        self.connection.connect()

    def disconnect(self) -> None:
        """Closes the connection to Q-SYS Core"""
        self.connection.disconnect()

    def login(self, username: str, password: str) -> None:
        """Authenticates with Q-SYS Core"""
        response = self._send_command("Logon", {
            "User": username,
            "Password": password
        })
        
        if response.error:
            raise AuthenticationError(f"Login failed: {response.error}")

    def _send_command(self, method: str, params: Dict[str, Any]) -> QSYSResponse:
        """Sends a command and waits for response"""
        response_received = threading.Event()
        response_data = {}

        def callback(data: Dict[str, Any]):
            response_data.update(data)
            response_received.set()

        self.connection.send_command(method, params, callback)
        response_received.wait(timeout=5.0)  # 5 second timeout
        print(f"Received: {response_data}")

        return QSYSResponse.from_dict(response_data)

# Example usage:
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Create client instance
    client = QSYSClient(
        host=os.getenv("QSYS_HOST", "localhost"),
        port=int(os.getenv("QSYS_PORT", "1710"))
    )

    try:
        # Connect to Q-SYS Core
        client.connect()

        # Login
        client.login(
            username=os.getenv("QSYS_USERNAME"),
            password=os.getenv("QSYS_PASSWORD")
        )

        # Check engine status
        response = client._send_command("StatusGet", {})
        print(f"Engine Status: {response.result}")

        # Create a change group with all MyGain controls
        response = client._send_command("ChangeGroup.AddComponentControl", {
            "Id": "main_controls",
            "Component": {
                "Name": "MyGain",
                "Controls": [
                    {"Name": "gain"},
                    {"Name": "mute"},
                    {"Name": "bypass"},
                    {"Name": "invert"}
                ]
            }
        })
        print(f"Add component response: {response.result}")

        # Set up auto-polling with fixed rate
        response = client._send_command("ChangeGroup.AutoPoll", {
            "Id": "main_controls",
            "Rate": 1.0
        })
        print(f"AutoPoll setup response: {response.result}")

        # Keep the program running
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        client.disconnect()