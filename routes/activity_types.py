from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from schemas.activity import ActivityType as ActivityTypeSchema, ActivityTypeCreate
from services.activity import ActivityService
from exceptions.activity_type import ActivityTypeError

router = APIRouter()

@router.get("/", response_model=List[ActivityTypeSchema])
def get_activity_types(db: Session = Depends(get_db)):
    try:
        return ActivityService(db).get_activity_types()
    except ActivityTypeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/", response_model=ActivityTypeSchema)
def create_activity_type(
    activity_type: ActivityTypeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
):
    try:
        return ActivityService(db).create_activity_type(activity_type)
    except ActivityTypeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{activity_type_id}", response_model=ActivityTypeSchema)
def get_activity_type(activity_type_id: int, db: Session = Depends(get_db)):
    try:
        return ActivityService(db).get_activity_type(activity_type_id)
    except ActivityTypeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{activity_type_id}", response_model=ActivityTypeSchema)
def update_activity_type(
    activity_type_id: int,
    activity_type: ActivityTypeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
):
    try:
        return ActivityService(db).update_activity_type(activity_type_id, activity_type)
    except ActivityTypeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.delete("/{activity_type_id}", response_model=ActivityTypeSchema)
def delete_activity_type(
    activity_type_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
):
    try:
        activity_type = ActivityService(db).get_activity_type(activity_type_id)
        ActivityService(db).delete_activity_type(activity_type_id)
        return activity_type
    except ActivityTypeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)