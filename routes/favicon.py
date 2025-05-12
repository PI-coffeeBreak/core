from fastapi import APIRouter, Depends
from schemas.favicon import Favicon
from services.favicon import FaviconService

router = APIRouter()

@router.get("/", response_model=Favicon)
async def get_favicon(favicon_service: FaviconService = Depends()):
    """
    Get the current favicon URL
    """
    return await favicon_service.get_favicon()

@router.put("/", response_model=Favicon)
async def update_favicon(
    favicon: Favicon,
    favicon_service: FaviconService = Depends()
):
    """
    Update the favicon URL
    """
    await favicon_service.store_favicon(favicon)
    return favicon 