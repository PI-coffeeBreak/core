from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from bson import ObjectId


class BaseComponentSchema(BaseModel):
    name: str = Field(..., title="Component Name")
    component_id: Optional[str] = Field(
        default_factory=lambda: str(ObjectId()), title="Component ID")
    require_auth: bool = Field(
        default=False, title="Requires Authentication",
        description="Whether the component should require user authentication"
    )

    class Config:
        from_attributes = True
        extra = "allow"


class AddBaseComponentSchema(BaseModel):
    name: str = Field(..., title="Component Name")

    class Config:
        from_attributes = True
        extra = "allow"


class PageSchema(BaseModel):
    title: str = Field(..., title="Page Title")
    description: Optional[str] = Field(default=None, title="Page Description")
    enabled: bool = Field(default=True, title="Is Page Enabled")
    components: List[AddBaseComponentSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class Page(BaseModel):
    """
    Schema for a page with components
    """
    page_id: Optional[str] = Field(
        default_factory=lambda: str(ObjectId()), title="Page ID")
    title: str = Field(..., title="Page Title")
    description: Optional[str] = Field(default=None, title="Page Description")
    enabled: bool = Field(default=True, title="Is Page Enabled")
    components: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        from_attributes = True
        extra = "allow"


class PageResponse(BaseModel):
    page_id: str
    title: str
    description: Optional[str]
    enabled: bool
    components: List[BaseComponentSchema]

    class Config:
        from_attributes = True


class DeletePageResponse(BaseModel):
    page_id: str

    class Config:
        from_attributes = True


class RemoveComponentResponse(BaseModel):
    component_id: str

    class Config:
        from_attributes = True


class PagePatchSchema(BaseModel):
    """Schema for PATCH operations where all fields are optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    components: Optional[List[Dict[str, Any]]] = None
