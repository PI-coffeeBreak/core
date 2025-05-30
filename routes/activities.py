from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from schemas.activity import Activity as ActivitySchema, ActivityCreate
from schemas.activity_owner import ActivityOwner as ActivityOwnerSchema, ActivityOwnerCreate
from services.activity import ActivityService
from exceptions.activity import ActivityError

router = APIRouter()

@router.get("/", response_model=List[ActivitySchema])
def get_activities(db: Session = Depends(get_db)):
    return ActivityService(db).get_all()

@router.post("/", response_model=ActivitySchema)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db), _: dict = Depends(check_role(["manage_activities"]))):
    try:
        return ActivityService(db).create(activity)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/batch/", response_model=List[ActivitySchema])
def create_activities(activities: List[ActivityCreate], db: Session = Depends(get_db), _: dict = Depends(check_role(["manage_activities"]))):
    try:
        return ActivityService(db).create_many(activities)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    try:
        return ActivityService(db).get_by_id(activity_id)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.put("/{activity_id}", response_model=ActivitySchema)
def update_activity(activity_id: int, activity: ActivityCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    try:
        return ActivityService(db).update(activity_id, activity)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.delete("/{activity_id}", response_model=ActivitySchema)
def delete_activity(activity_id: int, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    try:
        activity = ActivityService(db).get_by_id(activity_id)
        ActivityService(db).delete(activity_id)
        return activity
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.delete("/{activity_id}/image", response_model=ActivitySchema)
def remove_activity_image(activity_id: int, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    try:
        return ActivityService(db).remove_image(activity_id)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.post("/{activity_id}/owners/", response_model=ActivityOwnerSchema)
def add_activity_owner(
    activity_id: int,
    owner: ActivityOwnerCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
):
    try:
        return ActivityService(db).add_owner(activity_id, owner.user_id)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.delete("/{activity_id}/owners/{user_id}", response_model=ActivityOwnerSchema)
def remove_activity_owner(
    activity_id: int,
    user_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
):
    try:
        return ActivityService(db).remove_owner(activity_id, user_id)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

@router.get("/{activity_id}/owners/", response_model=List[ActivityOwnerSchema])
def get_activity_owners(
    activity_id: int,
    db: Session = Depends(get_db)
):
    try:
        return ActivityService(db).get_owners(activity_id)
    except ActivityError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)