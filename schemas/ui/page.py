from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class BaseComponentSchema(BaseModel):
    name: str = Field(..., title="Component Name")
    component_id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), title="Component ID")

    class Config:
        from_atributes = True

class AddBaseComponentSchema(BaseModel):
    name: str = Field(..., title="Component Name")

    class Config:
        from_atributes = True
        
class PageSchema(BaseModel):
    title: str = Field(..., title="Page Title")
    components: List[AddBaseComponentSchema] = Field(default_factory=list)

    class Config:
        from_atributes = True

class PageResponse(BaseModel):
    page_id: str
    title: str
    components: List[BaseComponentSchema]

    class Config:
        from_atributes = True

class DeletePageResponse(BaseModel):
    page_id: str

    class Config:
        from_atributes = True

class RemoveComponentResponse(BaseModel):
    component_id: str

    class Config:
        from_atributes = True