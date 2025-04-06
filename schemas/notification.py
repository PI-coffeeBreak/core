from pydantic import BaseModel
from enum import Enum
from typing import List


class RecipientType(str, Enum):
    SINGLE = "SINGLE"
    GROUP = "GROUP"


class NotificationRequest(BaseModel):
    type: str
    recipient_type: RecipientType
    recipient: str
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
