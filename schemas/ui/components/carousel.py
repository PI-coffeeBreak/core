from typing import Annotated
from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.media import Media

class Carousel(BaseComponentSchema):
    """
    Schema for Carousel component
    """
    images: list[
        Annotated[str, Field(title="External URL")] | 
        Annotated[Media, Field(title="Upload Media")]
    ] = Field(
        ..., description="List of images to display in the carousel"
    )