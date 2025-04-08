from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.ui.color import TextColor


class Text(BaseComponentSchema):
    """
    Schema for Text component

    Attributes:
        content (str): The text content to be displayed
    """
    text: str = Field(..., description="The text content to be displayed")
    color: str = Field(
        default=TextColor.PRIMARY_CONTENT,
        description="Text color of the text",
        optional=True
    )
    italic: bool = Field(
        default=False,
        description="Whether the text should be italicized",
        optional=True
    )
    bold: bool = Field(
        default=False,
        description="Whether the text should be bold",
        optional=True
    )
    underline: bool = Field(
        default=False,
        description="Whether the text should be underlined",
        optional=True
    )
