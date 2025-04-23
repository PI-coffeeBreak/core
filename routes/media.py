from fastapi import APIRouter, Depends, UploadFile, File, Response, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import magic

from dependencies.database import get_db
from dependencies.auth import get_current_user, check_role
from services.media import MediaService
from schemas.media import MediaResponse

router = APIRouter()


@router.post("/register", response_model=MediaResponse)
async def register_media(
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(check_role(['customization']))
):
    """Register a new media object before upload"""
    return MediaService.register(db)


@router.post("/{uuid}", response_model=MediaResponse)
async def upload_media(
    uuid: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(lambda: get_current_user(force_auth=False))
):
    """Upload a new media file"""
    return MediaService.create(db, uuid, file.file, file.filename, user)


@router.get("/{uuid}")
async def download_media(
    uuid: str,
    db: Session = Depends(get_db)
):
    """Download a media file"""
    media, data = MediaService.read(db, uuid)

    # Read first chunk to detect MIME type
    chunk = data.read(2048)
    mime = magic.from_buffer(chunk, mime=True)
    data.seek(0)  # Reset file pointer

    # Determine if content should be displayed inline or downloaded
    content_disposition = "attachment"
    if mime.startswith(('image/', 'video/')):
        content_disposition = "inline"

    return StreamingResponse(
        data,
        media_type=mime,
        headers={
            "Content-Disposition": f'{content_disposition}; filename="{media.alias}"'
        }
    )


@router.put("/{uuid}", response_model=MediaResponse)
async def update_media(
    uuid: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(lambda: get_current_user(force_auth=False))
):
    """Update an existing media file"""
    return MediaService.create_or_replace(db, uuid, file.file, file.filename, user)


@router.delete("/{uuid}")
async def delete_media(
    uuid: str,
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(lambda: get_current_user(force_auth=False))
):
    """Delete a media file"""
    MediaService.remove(db, uuid, user)
    return {"message": "Media deleted successfully"}
