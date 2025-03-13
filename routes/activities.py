from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db
from models.activity import Activity
from schemas.activity import Activity as ActivitySchema, ActivityCreate

router = APIRouter()

@router.get("/")
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return activities

@router.post("/", response_model=ActivitySchema)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    new_activity = Activity(activity)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity
