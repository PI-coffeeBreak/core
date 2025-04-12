from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.database import get_db
from dependencies.auth import check_role
from models.event_info import Event as EventInfoModel
from schemas.event_info import EventInfo, EventInfoCreate, EventInfoBase, ImageUploadParams
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

@router.post("/event/image", response_model=EventInfo)
async def upload_event_image(
    request: Request,
    file: UploadFile = File(...),
    params: ImageUploadParams = Depends(),
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
    
    # Use the existing media UUID
    media_uuid = event.image_id
    
    # Validate file size and extension
    if file.size > params.max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum allowed size of {params.max_size} bytes."
        )
    if not any(file.filename.endswith(ext) for ext in params.allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed extensions: {params.allowed_extensions}."
        )
    
    # Update the existing media
    MediaService.create_or_replace(db, media_uuid, file.file, file.filename)
    
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