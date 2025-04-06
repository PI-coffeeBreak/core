from pydantic import BaseModel, Field
from schemas.ui.page import BaseComponentSchema
from schemas.ui.color import TextColor


class TitleComponent(BaseComponentSchema):
    """
    Schema for Title component

    Attributes:
        text (str): The text to be displayed
        className (str): CSS classes to be applied
    """
    text: str = Field(..., description="The text to be displayed")
    color: str = Field(
        default=TextColor.PRIMARY_CONTENT,
        description="Text color of the title",
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
