from fastapi import Depends, APIRouter, HTTPException
import schemas.ui.page as page_schema
from dependencies.auth import check_role
from bson import ObjectId
from services.ui.page_service import page_service
from typing import List
import logging

logger = logging.getLogger("coffeebreak.core")

router = APIRouter()


@router.post("/", response_model=page_schema.PageResponse, summary="Create a new page")
async def create_page(page: page_schema.PageSchema, user_info: dict = Depends(check_role(["customization"]))):
    logger.debug("Creating new page")
    components_with_id = [
        {**c.dict(), "component_id": str(ObjectId())} for c in page.components
    ]
    page_id = await page_service.create_page(
        title=page.title,
        description=page.description,
        enabled=page.enabled,
        components=components_with_id
    )
    return {
        "page_id": page_id,
        "title": page.title,
        "description": page.description,
        "enabled": page.enabled,
        "components": components_with_id
    }


@router.put("/{page_id}", response_model=page_schema.PageResponse, summary="Update an existing page")
async def update_page(page_id: str, page: page_schema.PageSchema, user_info: dict = Depends(check_role(["customization"]))):
    logger.debug("Updating page")
    updated = await page_service.update_page(page_id, page.title, [c.dict() for c in page.components])
    if not updated:
        logger.error("Failed to update page")
        raise HTTPException(status_code=404, detail="Error updating page")
    return {"page_id": page_id,
            "title": page.title,
            "description": page.description,
            "enabled": page.enabled,
            "components": page.components
            }


@router.delete("/{page_id}", response_model=page_schema.DeletePageResponse, summary="Delete a page by its ID")
async def delete_page(page_id: str, user_info: dict = Depends(check_role(["customization"]))):
    logger.debug("Deleting page")
    deleted = await page_service.delete_page(page_id)
    if not deleted:
        logger.error("Failed to delete page")
        raise HTTPException(status_code=404, detail="Error deleting page")
    return {"page_id": page_id}


@router.get("/", response_model=List[page_schema.PageResponse], summary="List all enabled pages")
async def list_pages():
    logger.debug("Listing all pages")
    pages = await page_service.list_pages()
    logger.debug(f"Found {len(pages)} pages")
    return [
        {
            "page_id": page["id"],
            "title": page["title"],
            "description": page["description"],
            "enabled": page["enabled"],
            "components": page["components"]
        }
        for page in pages if page.get("enabled", False) is True
    ]

@router.get("/all/", response_model=List[page_schema.PageResponse], summary="List all pages (enabled and disabled)")
async def list_all_pages():
    logger.debug("Listing all pages (enabled and disabled)")
    pages = await page_service.list_pages()
    return [
        {
            "page_id": page["id"],
            "title": page["title"],
            "description": page["description"],
            "enabled": page["enabled"],
            "components": page["components"]
        }
        for page in pages
    ]

@router.get("/{page_id}", response_model=page_schema.PageResponse, summary="Get a page by its ID")
async def get_page(page_id: str):
    logger.debug(f"Getting page {page_id}")
    page = await page_service.get_page(page_id)
    if not page:
        logger.error("Page not found")
        raise HTTPException(status_code=404, detail="Error getting page")
    return {
        "page_id": page["id"],
        "title": page["title"],
        "description": page["description"],
        "enabled": page["enabled"],
        "components": page["components"]
    }


@router.post("/{page_id}/components/", response_model=page_schema.BaseComponentSchema, summary="Add a new component to the page")
async def add_component(page_id: str, component: page_schema.AddBaseComponentSchema, user_info: dict = Depends(check_role(["customization"]))):
    component_dict = component.dict()
    component_dict['component_id'] = str(ObjectId())
    added = await page_service.add_component(page_id, component_dict)
    if not added:
        raise HTTPException(status_code=404, detail="Error adding component")
    return {"name": component.name, "component_id": component_dict['component_id']}


@router.delete("/{page_id}/components/{component_id}", response_model=page_schema.RemoveComponentResponse, summary="Remove a specific component")
async def remove_component(page_id: str, component_id: str, user_info: dict = Depends(check_role(["customization"]))):
    removed = await page_service.remove_component(page_id, component_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Error removing component")
    return {"component_id": component_id}


@router.put("/{page_id}/components/{component_id}", response_model=page_schema.BaseComponentSchema, summary="Update a specific component")
async def update_component(page_id: str, component_id: str, updated_component: page_schema.AddBaseComponentSchema, user_info: dict = Depends(check_role(["customization"]))):
    updated = await page_service.update_component(page_id, component_id, updated_component.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Error updating component")
    return {"component_id": component_id, "name": updated_component.name}


@router.patch("/{page_id}", response_model=page_schema.PageResponse)
async def patch_page(
    page_id: str,
    page: page_schema.PagePatchSchema,
    user_info: dict = Depends(check_role(["customization"]))
):
    """Update specific fields of a page."""
    logger.debug(f"Patching page {page_id}")

    current_page = await page_service.get_page(page_id)
    if not current_page:
        raise HTTPException(status_code=404, detail="Page not found")

    updated = await page_service.update_page(
        page_id,
        page.title if page.title is not None else current_page["title"],
        page.components if page.components is not None else current_page["components"],
        enabled=page.enabled if page.enabled is not None else current_page["enabled"]
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Error updating page")

    updated_page = await page_service.get_page(page_id)
    return {
        "page_id": updated_page["id"],
        "title": updated_page["title"],
        "description": updated_page["description"],
        "enabled": updated_page["enabled"],
        "components": updated_page["components"]
    }
