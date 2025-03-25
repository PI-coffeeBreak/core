from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from models.activity import Activity
from schemas.activity import Activity as ActivitySchema, ActivityCreate

router = APIRouter()

@router.get("/", response_model=List[ActivitySchema])
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return activities

@router.post("/", response_model=ActivitySchema)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    new_activity = Activity(**activity.model_dump())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.post("/batch", response_model=List[ActivitySchema])
def create_activities(activities: List[ActivityCreate], db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    new_activities = [Activity(**activity.model_dump()) for activity in activities]
    
    db.add_all(new_activities)
    db.commit()

    for activity in new_activities:
        db.refresh(activity)
    return new_activities

@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/{activity_id}", response_model=ActivitySchema)
def update_activity(activity_id: int, activity: ActivityCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    for key, value in activity.dict().items():
        setattr(db_activity, key, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}", response_model=ActivitySchema)
def delete_activity(activity_id: int, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(db_activity)
    db.commit()
    return db_activity