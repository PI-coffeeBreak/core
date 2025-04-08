from pydantic import Field
from schemas.ui.page import BaseComponentSchema


class Image(BaseComponentSchema):
    """
    Schema for Image component

    Attributes:
        src (str): The source URL of the image
        alt (str): Alternative text for the image
    """
    src: str = Field(..., description="The source URL of the image")
    alt: str = Field(..., description="Alternative text for the image")
    className: str = Field(
        default="",
        description="CSS classes to be applied",
        optional=True
    )
