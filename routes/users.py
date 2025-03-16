from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db
from models.user import User
from schemas.user import User as UserSchema, UserCreate
from dependencies.auth import get_current_user, check_role

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/im/organizer")
async def im_organizer(current_user: dict = Depends(check_role(["organizer"]))):
    return current_user
