from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.database import get_db
from dependencies.auth import check_role
from models.event_info import Event as EventInfoModel
from schemas.event_info import EventInfo, EventInfoCreate, EventInfoBase
from services.media import MediaService

router = APIRouter()

# Helper to build image URL
def get_image_url(request: Request, media_uuid: str) -> Optional[str]:
    if not media_uuid:
        return None
    return f"{request.base_url}media/{media_uuid}"

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
    
    # Create response with image URL
    response = EventInfo.model_validate(event)
    if event.image_id:
        response.image_url = get_image_url(request, event.image_id)
    
    return response

@router.post("/event", response_model=EventInfo, status_code=status.HTTP_201_CREATED, summary="Create or update event information")
async def create_or_update_event(
    request: Request,
    event: EventInfoCreate, 
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["admin", "events_manager"]))
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
        
        # Create response with image URL
        response = EventInfo.model_validate(existing_event)
        if existing_event.image_id:
            response.image_url = get_image_url(request, existing_event.image_id)
        
        return response
    else:
        # Create new event
        db_event = EventInfoModel(**event.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Create response with image URL
        response = EventInfo.model_validate(db_event)
        if db_event.image_id:
            response.image_url = get_image_url(request, db_event.image_id)
        
        return response

@router.post("/event/image", response_model=EventInfo, summary="Upload event image")
async def upload_event_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["admin", "events_manager"]))
):
    """
    Upload or update the event image.
    """
    # Get the current event
    event = db.query(EventInfoModel).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No event found. Create event first."
        )
    
    # If there's already an image, prepare to replace it
    if event.image_id:
        # Use the existing media UUID
        media_uuid = event.image_id
        
        # Update the existing media
        MediaService.create_or_replace(db, media_uuid, file.file, file.filename)
    else:
        # Register new media with acceptable image extensions
        media = MediaService.register(
            db,
            max_size=10 * 1024 * 1024,  # 10MB limit
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            alias=file.filename
        )
        
        # Store the media UUID
        media_uuid = media.uuid
        
        # Create the actual media content
        MediaService.create(db, media_uuid, file.file, file.filename)
        
        # Update the event with the new media UUID
        event.image_id = media_uuid
        db.commit()
        db.refresh(event)
    
    # Create response with image URL
    response = EventInfo.model_validate(event)
    response.image_url = get_image_url(request, media_uuid)
    
    return response

@router.delete("/event/image", response_model=EventInfo, summary="Delete event image")
async def delete_event_image(
    request: Request,
    db: Session = Depends(get_db),
    user_info: dict = Depends(check_role(["admin", "events_manager"]))
):
    """
    Delete the event image.
    """
    # Get the current event
    event = db.query(EventInfoModel).first()
    if not event or not event.image_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No event image found."
        )
    
    # Remove the media file
    MediaService.remove(db, event.image_id, user_info)
    
    # Clear the image reference
    event.image_id = None
    db.commit()
    db.refresh(event)
    
    # Return the updated event
    response = EventInfo.model_validate(event)
    return response