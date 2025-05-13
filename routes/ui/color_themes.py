from fastapi import APIRouter, HTTPException
from schemas.ui.color_theme import ColorTheme
from dependencies.mongodb import db
from services.manifest import ManifestService

router = APIRouter()
manifest_service = ManifestService()

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
    
    # Update the manifest
    manifest = await manifest_service.get_manifest()
    manifest['theme_color'] = color_theme.primary
    manifest['background_color'] = color_theme.base_100
    await manifest_service.update_manifest(manifest)
    return updated_theme
