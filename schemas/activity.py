from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ActivityTypeBase(BaseModel):
    type: str

class ActivityTypeCreate(ActivityTypeBase):
    pass

class ActivityType(ActivityTypeBase):
    id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ActivityBase(BaseModel):
    name: str
    description: str
    image: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
    type_id: int

    topic: Optional[str] = None
    speaker: Optional[str] = None
    facilitator: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ActivityList(BaseModel):
    activities: List[Activity]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
