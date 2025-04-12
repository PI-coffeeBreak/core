from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class EventInfoBase(BaseModel):
    """
    Base schema for event information
    """
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    image_id: Optional[str] = None

class EventInfoCreate(EventInfoBase):
    """
    Schema for creating new event information
    """
    pass

class EventInfo(EventInfoBase):
    """
    Schema for event information response
    """
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True