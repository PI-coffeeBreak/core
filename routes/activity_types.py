from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from models.activity import ActivityType
from schemas.activity import ActivityType as ActivityTypeSchema, ActivityTypeCreate

router = APIRouter()

@router.get("/", response_model=List[ActivityTypeSchema])
def get_activity_types(db: Session = Depends(get_db)):
    activity_types = db.query(ActivityType).all()
    return activity_types

@router.post("/", response_model=ActivityTypeSchema)
def create_activity_type(activity_type: ActivityTypeCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    new_activity_type = ActivityType(**activity_type.dict())
    db.add(new_activity_type)
    db.commit()
    db.refresh(new_activity_type)
    return new_activity_type

@router.get("/{activity_type_id}", response_model=ActivityTypeSchema)
def get_activity_type(activity_type_id: int, db: Session = Depends(get_db)):
    activity_type = db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    if activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    return activity_type

@router.put("/{activity_type_id}", response_model=ActivityTypeSchema)
def update_activity_type(activity_type_id: int, activity_type: ActivityTypeCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    db_activity_type = db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    if db_activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    for key, value in activity_type.dict().items():
        setattr(db_activity_type, key, value)
    db.commit()
    db.refresh(db_activity_type)
    return db_activity_type

@router.delete("/{activity_type_id}", response_model=ActivityTypeSchema)
def delete_activity_type(activity_type_id: int, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    db_activity_type = db.query(ActivityType).filter(ActivityType.id == activity_type_id).first()
    if db_activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    db.delete(db_activity_type)
    db.commit()
    return db_activity_type