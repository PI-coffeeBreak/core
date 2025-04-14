from typing import Union
from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.media import Media


class Image(BaseComponentSchema):
    """
    Schema for Image component

    Attributes:
        src (Union[str, Media]): The source URL of the image (can be an external URL or a Media reference)
        alt (str): Alternative text for the image
    """
    src: Union[str, Media] = Field(
        ..., description="The source URL of the image (can be an external URL or a Media reference)")
    alt: str = Field(..., description="Alternative text for the image")
    className: str = Field(
        default="",
        description="CSS classes to be applied",
        optional=True
    )
