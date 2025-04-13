from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from dependencies.database import get_db
from dependencies.auth import check_role
from models.event_info import Event as EventInfoModel
from schemas.event_info import EventInfo, EventInfoCreate, EventInfoCreateFirstUser
from services.media import MediaService
from services.user_service import assign_role_to_user

router = APIRouter()


@router.get("/event", response_model=EventInfo, summary="Get current event information")
async def get_event(request: Request, db: Session = Depends(get_db)):
    event = db.query(EventInfoModel).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No event information found")

    return EventInfo.model_validate(event)


@router.post("/event", response_model=EventInfo, status_code=status.HTTP_201_CREATED, summary="Create or update event information (public, one-time)")
async def create_event_first_time(
    event: EventInfoCreateFirstUser,
    request: Request,
    db: Session = Depends(get_db)
):
    existing_event = db.query(EventInfoModel).first()
    if existing_event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event already exists")

    if not event.first_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="First user ID is required")

    media = MediaService.register(
        db=db,
        max_size=50 * 1024 * 1024,
        allows_rewrite=True,
        valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        alias="event_image"
    )

    db_event = EventInfoModel(**event.model_dump(exclude={"first_user_id"}), image_id=media.uuid)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Assign cb-organizer role to first user
    await assign_role_to_user(event.first_user_id, "cb-organizer")

    return EventInfo.model_validate(db_event)


@router.post("/event/admin", response_model=EventInfo, status_code=status.HTTP_201_CREATED, summary="Create or update event information (admin only)")
async def create_or_update_event_admin(
    request: Request,
    event: EventInfoCreate,
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["admin", "manage_event"]))
):
    existing_event = db.query(EventInfoModel).first()

    if existing_event:
        for key, value in event.model_dump(exclude={"first_user_id"}).items():
            setattr(existing_event, key, value)
        db.commit()
        db.refresh(existing_event)
        return EventInfo.model_validate(existing_event)

    media = MediaService.register(
        db=db,
        max_size=50 * 1024 * 1024,
        allows_rewrite=True,
        valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        alias="event_image"
    )

    db_event = EventInfoModel(**event.model_dump(exclude={"first_user_id"}), image_id=media.uuid)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return EventInfo.model_validate(db_event)


@router.get("/event/image", summary="Get current event image")
async def get_event_image(
    request: Request,
    db: Session = Depends(get_db)
):
    event = db.query(EventInfoModel).first()
    if not event or not event.image_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No event image found")

    return RedirectResponse(url=f"/media/{event.image_id}")