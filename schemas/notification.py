from pydantic import BaseModel, field_serializer
from enum import Enum
from typing import List, Dict, Union, Optional
from datetime import datetime


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
    recipient_type: RecipientType
    recipient: Optional[str] = None
    payload: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.isoformat()

    class Config:
        from_attributes = True
