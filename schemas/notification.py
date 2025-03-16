from pydantic import BaseModel
from enum import Enum

class RecipientType(str, Enum):
    SINGLE = "SINGLE"
    GROUP = "GROUP"

class NotificationRequest(BaseModel):
    type: str
    recipient_type: RecipientType
    recipient: int
    payload: str
    priority: int