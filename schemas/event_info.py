from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EventInfoBase(BaseModel):
    """
    Base schema for event information
    """
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str


class EventInfoCreate(EventInfoBase):
    """
    Schema for creating new event information
    """
    pass

class EventInfoCreateFirstUser(EventInfoBase):
    """
    Schema for creating new event information with first user ID
    """
    first_user_id: str

class EventInfo(EventInfoBase):
    """
    Schema for event information response
    """
    id: int
    image_id: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
