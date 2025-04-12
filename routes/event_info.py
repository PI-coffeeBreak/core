from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from dependencies.database import get_db
from dependencies.auth import check_role
from models.event_info import Event as EventInfoModel
from schemas.event_info import EventInfo, EventInfoCreate
from services.media import MediaService

router = APIRouter()


@router.get("/event", response_model=EventInfo, summary="Get current event information")
async def get_event(request: Request, db: Session = Depends(get_db)):
    """
    Get information about the current event.
    """
    event = db.query(EventInfoModel).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No event information found"
        )

    return EventInfo.model_validate(event)


@router.post("/event", response_model=EventInfo, status_code=status.HTTP_201_CREATED, summary="Create or update event information")
async def create_or_update_event(
    request: Request,
    event: EventInfoCreate,
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["admin", "manage_event"]))
):
    """
    Create or update the event information.
    If event information already exists, it will be updated.
    """
    # Check if event already exists
    existing_event = db.query(EventInfoModel).first()

    if existing_event:
        # Update existing event
        for key, value in event.model_dump().items():
            setattr(existing_event, key, value)
        db.commit()
        db.refresh(existing_event)
        return EventInfo.model_validate(existing_event)
    else:
        # Create new event
        event_dict = event.model_dump()

        # Register media for image
        media = MediaService.register(
            db=db,
            max_size=50 * 1024 * 1024,  # 50MB
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            alias="event_image"
        )

        # Create event with media id
        db_event = EventInfoModel(**event_dict, image_id=media.uuid)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return EventInfo.model_validate(db_event)


@router.get("/event/image", summary="Get current event image")
async def get_event_image(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get the current event image.
    This is an alias for /media/<image_id> that automatically redirects to the current event's image.
    """
    event = db.query(EventInfoModel).first()
    if not event or not event.image_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No event image found"
        )

    return RedirectResponse(url=f"/media/{event.image_id}")
