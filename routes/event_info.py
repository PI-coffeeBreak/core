from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from dependencies.database import get_db
from dependencies.auth import check_role
from models.event_info import Event as EventInfoModel
from schemas.event_info import EventInfo, EventInfoCreate, EventInfoCreateFirstUser
from services.media import MediaService
from services.user_service import assign_role_to_user
from services.manifest import ManifestService

router = APIRouter()
manifest_service = ManifestService()

@router.get("/event", 
    response_model=EventInfo, 
    summary="Get current event information",
    description="Retrieves the current event details including name, description, and image information.",
    responses={
        200: {
            "description": "Successfully retrieved event information",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Coffee Break 2024",
                        "description": "Annual coffee break event",
                        "image_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        404: {
            "description": "No event information found"
        }
    })
async def get_event(request: Request, db: Session = Depends(get_db)):
    event = db.query(EventInfoModel).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No event information found")

    return EventInfo.model_validate(event)


@router.post("/event", 
    response_model=EventInfo, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create event information (public, one-time)",
    description="""Creates the initial event information. This endpoint can only be used once.
    It will:
    - Create the event record
    - Set up image storage
    - Assign the cb-organizer role to the first user
    - Update the PWA manifest with event details""",
    responses={
        201: {
            "description": "Event information created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Coffee Break 2025",
                        "description": "Annual coffee break event",
                        "image_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        400: {
            "description": "Event information already exists"
        }
    })
async def create_event(
    event: EventInfoCreateFirstUser,
    request: Request,
    db: Session = Depends(get_db)
):
    existing_event = db.query(EventInfoModel).first()
    if existing_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Event already exists")

    media = MediaService.register(
        db=db,
        max_size=50 * 1024 * 1024,
        allows_rewrite=True,
        valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        alias="event_image"
    )

    db_event = EventInfoModel(
        **event.model_dump(exclude={"first_user_id"}), image_id=media.uuid)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Assign cb-organizer role to first user
    await assign_role_to_user(event.first_user_id, "cb-organizer")

    # Update manifest with event information
    manifest = await manifest_service.get_manifest()
    manifest.name = event.name
    manifest.short_name = event.name
    manifest.description = event.description
    await manifest_service.update_manifest(manifest)

    return EventInfo.model_validate(db_event)


@router.put("/event", 
    response_model=EventInfo, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create or update event information (admin only)",
    description="""Creates or updates event information. Requires manage_event role.
    This endpoint will:
    - Create or update the event record
    - Update the PWA manifest with new event details
    - Handle image storage if needed""",
    responses={
        201: {
            "description": "Event information created or updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "name": "Coffee Break 2024",
                        "description": "Annual coffee break event",
                        "image_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        403: {
            "description": "Not authorized. Requires manage_event role"
        }
    })
async def create_or_update_event_admin(
    request: Request,
    event: EventInfoCreate,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(check_role(["manage_event"]))
):
    existing_event = db.query(EventInfoModel).first()

    # Update manifest with event information
    manifest = await manifest_service.get_manifest()
    manifest.name = event.name
    manifest.short_name = event.name
    manifest.description = event.description
    await manifest_service.update_manifest(manifest)

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

    db_event = EventInfoModel(
        **event.model_dump(exclude={"first_user_id"}), image_id=media.uuid)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return EventInfo.model_validate(db_event)


@router.get("/event/image", 
    summary="Get current event image",
    description="Returns a redirect to the current event's image. If no event or image exists, returns a 404 error.",
    responses={
        307: {
            "description": "Redirect to the event image URL"
        },
        404: {
            "description": "No event image found"
        }
    })
async def get_event_image(
    request: Request,
    db: Session = Depends(get_db)
):
    event = db.query(EventInfoModel).first()
    if not event or not event.image_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No event image found")

    return RedirectResponse(url=f"/media/{event.image_id}")
