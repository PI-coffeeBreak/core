from pydantic import BaseModel

class ActivityOwnerBase(BaseModel):
    activity_id: int
    user_id: str

class ActivityOwnerCreate(ActivityOwnerBase):
    pass

class ActivityOwner(ActivityOwnerBase):
    id: int

    class Config:
        from_attributes = True 