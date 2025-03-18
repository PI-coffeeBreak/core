from pydantic import BaseModel, Field
from typing import List

class BaseComponentSchema(BaseModel):
    name: str = Field(..., title="Component Name")

    class Config:
        from_atributes = True
        
class PageSchema(BaseModel):
    title: str = Field(..., title="Page Title")
    components: List[BaseComponentSchema] = Field(default_factory=list)

    class Config:
        from_atributes = True

class PageUpdateSchema(BaseModel):
    title: str | None = None
    components: List[BaseComponentSchema] | None = None

    class Config:
        from_atributes = True

class PageResponse(BaseModel):
    title: str
    components: List[BaseComponentSchema]

    class Config:
        from_atributes = True

class CreatePageResponse(BaseModel):
    message: str = "Page created successfully"
    page_id: str
    title: str
    components: List[BaseComponentSchema]

    class Config:
        from_atributes = True

class UpdatePageResponse(BaseModel):
    message: str = "Page updated successfully"
    page_id: str
    title: str
    components: List[BaseComponentSchema]

    class Config:
        from_atributes = True

class DeletePageResponse(BaseModel):
    message: str = "Page deleted successfully"
    page_id: str

    class Config:
        from_atributes = True

class AddComponentResponse(BaseModel):
    message: str = "Component added successfully"
    name: str = "Component Name"

    class Config:
        from_atributes = True

class RemoveComponentResponse(BaseModel):
    message: str = "Component removed successfully"
    name: str = "Component Name"

    class Config:
        from_atributes = True

class UpdateComponentResponse(BaseModel):
    message: str = "Component updated successfully"
    name: str = "Component Name"

    class Config:
        from_atributes = True