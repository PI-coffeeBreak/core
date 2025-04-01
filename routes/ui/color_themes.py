from fastapi import APIRouter, HTTPException
from schemas.ui.color_theme import ColorTheme
from dependencies.mongodb import db  # Assuming you are using MongoDB
from bson.objectid import ObjectId

router = APIRouter()


@router.get("/color-theme", response_model=ColorTheme)
async def get_color_theme():
    color_theme = await db['color_themes'].find_one()
    if not color_theme:
        raise HTTPException(status_code=404, detail="Color Theme not found")
    return color_theme


@router.put("/color-theme", response_model=ColorTheme)
async def update_color_theme(color_theme: ColorTheme):
    existing_theme = await db['color_themes'].find_one()
    if not existing_theme:
        raise HTTPException(status_code=404, detail="Color Theme not found")
    
    # Perform update
    updated_theme = await db['color_themes'].find_one_and_replace({}, color_theme.model_dump(), return_document=True)
    if not updated_theme:
        raise HTTPException(status_code=500, detail="Failed to update Color Theme")
    return updated_theme
