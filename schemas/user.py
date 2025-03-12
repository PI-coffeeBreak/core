from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Shared properties
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Schema for creating a user (excluding ID)
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[User]

    class Config:
        from_attributes = True
