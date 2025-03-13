from pydantic import BaseModel
from typing import Optional, List

class ActivityBase(BaseModel):
    name: str
    description: str
    type: str

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True

class ActivityList(BaseModel):
    activities: List[Activity]

    class Config:
        from_attributes = True