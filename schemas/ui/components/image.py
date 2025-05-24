from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.media import Media
from typing import Annotated


class Image(BaseComponentSchema):
    """
    Schema for Image component

    Attributes:
        src (Union[str, Media]): The source URL of the image (can be an external URL or a Media reference)
        alt (str): Alternative text for the image
    """
    src: Annotated[str, Field(title="External URL")] | Annotated[Media, Field(title="Upload Media")] = Field(
        ..., description="The source URL of the image (can be an external URL or a Media reference)"
    )
    alt: str = Field(..., description="Alternative text for the image")
