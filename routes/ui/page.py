from fastapi import Depends, APIRouter, HTTPException
from models.ui.page import page_model
from schemas.ui.page import PageSchema, BaseComponentSchema, CreatePageResponse, UpdatePageResponse, DeletePageResponse, PageResponse, AddComponentResponse, RemoveComponentResponse, UpdateComponentResponse
from dependencies.auth import check_role

router = APIRouter()

@router.post("/", response_model=CreatePageResponse, summary="Create a new page")
async def create_page(page: PageSchema, user_info: dict = Depends(check_role(["customization"]))):
    page_id = await page_model.create_page(page.title, [c.dict() for c in page.components])
    return {"message": "Page created successfully", "page_id": page_id, "title": page.title, "components": page.components}


@router.put("/{page_id}", response_model=UpdatePageResponse, summary="Update an existing page")
async def update_page(page_id: str, page: PageSchema, user_info: dict = Depends(check_role(["customization"]))):
    updated = await page_model.update_page(page_id, page.title, [c.dict() for c in page.components])
    if not updated:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page updated successfully","page_id": page_id, "title": page.title, "components": page.components}


@router.delete("/{page_id}", response_model=DeletePageResponse, summary="Delete a page by its ID")
async def delete_page(page_id: str, user_info: dict = Depends(check_role(["customization"]))):
    deleted = await page_model.delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted successfully", "page_id": page_id}


@router.get("/{page_id}", response_model=PageResponse, summary="Get a page by its ID")
async def get_page(page_id: str):
    page = await page_model.get_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"title": page["title"], "components": page["components"]}


@router.post("/{page_id}/components", response_model=AddComponentResponse, summary="Add a new component to the page")
async def add_component(page_id: str, component: BaseComponentSchema, user_info: dict = Depends(check_role(["customization"]))):
    added = await page_model.add_component(page_id, component.dict())
    if not added:
        raise HTTPException(status_code=404, detail="Component not found")
    return {"message": "Component added successfully", "name": component.name}


@router.delete("/{page_id}/components/{component_name}", response_model=RemoveComponentResponse, summary="Remove a specific component")
async def remove_component(page_id: str, component_name: str, user_info: dict = Depends(check_role(["customization"]))):
    removed = await page_model.remove_component(page_id, component_name)
    if not removed:
        raise HTTPException(status_code=404, detail="Component not found")
    return {"message": "Component removed successfully", "name": component_name}


@router.put("/{page_id}/components/{component_name}", response_model=UpdateComponentResponse, summary="Update a specific component")
async def update_component(page_id: str, component_name: str, updated_component: BaseComponentSchema, user_info: dict = Depends(check_role(["customization"]))):
    updated = await page_model.update_component(page_id, component_name, updated_component.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Component not found")
    return {"message": "Component updated successfully", "name": component_name}