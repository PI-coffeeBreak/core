from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Shared properties
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Schema for creating a user (excluding ID)
class UserCreate(UserBase):
    firstName: str
    lastName: str
    enabled: bool

class User(UserBase):
    id: str
    firstName: str
    lastName: str
    emailVerified: bool
    createdTimestamp: int
    enabled: bool
    totp: bool
    disableableCredentialTypes: List[str]
    requiredActions: List[str]
    notBefore: int
    access: dict
    is_active: bool = True

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[User]

    class Config:
        from_attributes = True
