from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from models.activity import Activity
from schemas.activity import Activity as ActivitySchema, ActivityCreate
from services.media import MediaService
from utils.media import is_valid_url, is_valid_uuid, slugify
from uuid import uuid4

router = APIRouter()

@router.get("/", response_model=List[ActivitySchema])
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return activities

@router.post("/", response_model=ActivitySchema)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    image = activity.image

    if not image or not is_valid_url(image):
        media = MediaService.register(
            db=db,
            max_size=10 * 1024 * 1024,
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
            alias=f"{slugify(activity.name)}-{uuid4()}"
        )
        image = media.uuid

    new_activity = Activity(**activity.model_dump(exclude={"image"}), image=image)
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.post("/batch", response_model=List[ActivitySchema])
def create_activities(activities: List[ActivityCreate], db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    new_activities = []
    for activity in activities:
        image = activity.image

        if not image or not is_valid_url(image):
            media = MediaService.register(
                db=db,
                max_size=10 * 1024 * 1024,
                allows_rewrite=True,
                valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
                alias=f"{slugify(activity.name)}-{uuid4()}"
            )
            image = media.uuid

        new_activities.append(Activity(**activity.model_dump(exclude={"image"}), image=image))

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

    update_data = activity.dict(exclude_unset=True)
    new_image = update_data.get("image")

    if new_image:
        if is_valid_uuid(db_activity.image) and is_valid_url(new_image):
            MediaService.unregister(db, db_activity.image, force=True)
        elif is_valid_uuid(db_activity.image) and not is_valid_url(new_image):
            update_data.pop("image", None)
        elif is_valid_url(db_activity.image) and not is_valid_url(new_image):
            media = MediaService.register(
                db=db,
                max_size=10 * 1024 * 1024,
                allows_rewrite=True,
                valid_extensions=['.jpg', '.jpeg', '.png', '.webp'],
                alias=f"{slugify(db_activity.name)}-{uuid4()}"
            )
            update_data["image"] = media.uuid

    for key, value in update_data.items():
        setattr(db_activity, key, value)

    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}", response_model=ActivitySchema)
def delete_activity(activity_id: int, db: Session = Depends(get_db), user: dict = Depends(check_role(["manage_activities"]))):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    if is_valid_uuid(db_activity.image):
        MediaService.unregister(db, db_activity.image, force=True)

    db.delete(db_activity)
    db.commit()
    return db_activity

@router.delete("/{activity_id}/image", response_model=ActivitySchema)
def remove_activity_image(
    activity_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(check_role(["manage_activities"]))
):
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    if is_valid_uuid(db_activity.image):
        MediaService.unregister(db, db_activity.image, force=True)
    else:
        raise HTTPException(status_code=404, detail="Image is external or was not found")

    db_activity.image = None
    db.commit()
    db.refresh(db_activity)
    return db_activity