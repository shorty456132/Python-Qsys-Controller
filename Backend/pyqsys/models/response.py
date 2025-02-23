from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class QSYSResponse:
    """Represents a response from the Q-SYS Core"""
    jsonrpc: str
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QSYSResponse':
        return cls(
            jsonrpc=data.get('jsonrpc'),
            id=data.get('id'),
            result=data.get('result'),
            error=data.get('error')
        )