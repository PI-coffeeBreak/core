from typing import Optional, List
from pydantic import BaseModel, Field


class MediaBase(BaseModel):
    """
    Base schema for media attributes
    """
    max_size: Optional[int] = None
    alias: Optional[str] = None
    valid_extensions: List[str] = Field(default_factory=list)
    allow_rewrite: bool = True
    op_required: bool = False


class MediaCreate(MediaBase):
    """
    Schema for creating new media registration
    """
    pass


class MediaResponse(MediaBase):
    """
    Schema for media response
    """
    uuid: str
    hash: Optional[str] = None

    class Config:
        """Configure Pydantic to read data from ORM"""
        from_attributes = True
