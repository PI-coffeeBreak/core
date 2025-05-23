from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from dependencies.auth import check_role
from services.manifest import ManifestService
from schemas.manifest import InsertIcon, Manifest, Icon
from exceptions.manifest import ManifestNotFoundError, ManifestUpdateError, ManifestInsertIconError

router = APIRouter()
manifest_service = ManifestService()

@router.get("/manifest.json", response_model=Manifest, 
    summary="Get PWA manifest",
    description="Retrieves the current PWA manifest configuration. This is used by browsers to configure the PWA installation.")
async def get_manifest():
    try:
        manifest = await manifest_service.get_manifest()
        return manifest
    except ManifestNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/manifest.json", response_model=Manifest,
    summary="Update PWA manifest",
    description="Updates the PWA manifest configuration. Requires manage_event role.",
    status_code=200)
async def update_manifest(new_manifest: Manifest, _current_user: dict = Depends(check_role(["manage_event"]))):
    try:
        updated_manifest = await manifest_service.update_manifest(new_manifest)
        return updated_manifest
    except ManifestNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ManifestUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manifest/icon", response_model=Manifest,
    summary="Add icon to manifest",
    description="Adds a new icon to the PWA manifest. Creates both 'any' and 'maskable' versions. Requires manage_event role.",
    status_code=201)
async def insert_icon(icon: InsertIcon, _current_user: dict = Depends(check_role(["manage_event"]))):
    try:
        _inserted_icon = await manifest_service.insert_icon(Icon(**icon.model_dump(), purpose="any"))
        _inserted_maskable_icon = await manifest_service.insert_icon(Icon(**icon.model_dump(), purpose="maskable"))

        return await manifest_service.get_manifest()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))