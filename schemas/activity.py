from pydantic import BaseModel
from typing import Optional, List

class ActivityBase(BaseModel):
    title: str
    description: str

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