from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class EventInfoBase(BaseModel):
    """
    Base schema for event information
    """
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    image_id: Optional[str] = None

class EventInfoCreate(EventInfoBase):
    """
    Schema for creating new event information
    """
    pass

class EventInfo(EventInfoBase):
    """
    Schema for event information response
    """
    id: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ImageUploadParams(BaseModel):
    """Parameters for image upload"""
    max_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes"
    )
    allowed_extensions: list[str] = Field(
        default=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        description="List of allowed file extensions"
    )