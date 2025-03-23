from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.user import User as UserSchema, UserCreate
from dependencies.auth import get_current_user, check_role

router = APIRouter()

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/im/organizer")
async def im_organizer(current_user: dict = Depends(check_role(["organizer"]))):
    return current_user
