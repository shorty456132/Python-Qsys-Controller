from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ChangeGroup:
    """Represents a Change Group in Q-SYS"""
    id: str
    controls: List[str]
    auto_poll_rate: Optional[float] = None

    def to_dict(self):
        return {
            "Id": self.id,
            "Controls": self.controls
        }