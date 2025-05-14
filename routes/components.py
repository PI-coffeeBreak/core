from typing import Dict, Type
from fastapi import APIRouter, HTTPException
from schemas.ui.page import BaseComponentSchema
from services.component_registry import ComponentRegistry
from schemas.components import ComponentInfo, ComponentsList


router = APIRouter()


@router.get("/", response_model=ComponentsList)
async def list_components():
    """
    List all registered UI components and their schemas
    """
    components = ComponentRegistry.list_components()
    return ComponentsList(
        components={
            name: component.schema()
            for name, component in components.items()
        }
    )


@router.get("/{component_name}", response_model=ComponentInfo)
async def get_component(component_name: str):
    """
    Get schema information for a specific component
    """
    component = ComponentRegistry.get_component(component_name)
    if not component:
        raise HTTPException(
            status_code=404,
            detail=f"Component {component_name} not found"
        )

    return ComponentInfo(
        name=component_name,
        schema=component.schema()
    )
