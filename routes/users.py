from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db
from models.user import User
from schemas.user import User as UserSchema, UserCreate

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
