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


class Media(BaseModel):
    """
    Schema that represents a media reference through its UUID
    """
    uuid: str = Field(..., description="The UUID of the media")

    def __str__(self) -> str:
        return self.uuid
