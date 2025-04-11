from pydantic import BaseModel
from enum import Enum
from typing import List, Dict, Union, Optional


class RecipientType(str, Enum):
    UNICAST = "UNICAST"
    MULTICAST = "MULTICAST"
    BROADCAST = "BROADCAST"


class NotificationRequest(BaseModel):
    type: str
    recipient_type: RecipientType
    recipient: Optional[str] = None  # Can be None for BROADCAST
    payload: str
    priority: int

    def __repr__(self) -> str:
        # Returns a formatted string representation of the notification request
        return f"NotificationRequest(type={self.type}, recipient_type={self.recipient_type}, recipient={self.recipient}, priority={self.priority})"


class NotificationResponse(BaseModel):
    id: int
    payload: str
    delivered: bool

    class Config:
        from_attributes = True
