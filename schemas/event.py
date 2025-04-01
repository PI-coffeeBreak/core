from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class EventType(str, Enum):
    ENDPOINT_CALL = "ENDPOINT_CALL"
    USER_LOGIN = "USER_LOGIN"
    ERROR_OCCURRENCE = "ERROR_OCCURRENCE"

class EventRequest(BaseModel):
    event_type: EventType
    timestamp: datetime
    payload: str
    details: dict