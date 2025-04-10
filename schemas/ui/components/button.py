from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.ui.color import BackgroundColor, TextColor
from enum import Enum

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class Button(BaseComponentSchema):
    """
    Schema for Button component

    Attributes:
        text (str): The text to be displayed on the button
        METHOD (str): The HTTP method to be used
        URL (str): The URL to be called when the button is clicked
    """
    text: str = Field(
        default="",
        description="The text to be displayed on the button"
    )
    METHOD: HTTPMethod = Field(
        default=HTTPMethod.GET,
        description="The HTTP method to be used"
    )
    URL: str = Field(
        default="",
        description="The URL to be called when the button is clicked"
    )
    className: str = Field(
        default="",
        description="CSS classes to be applied",
        optional=True
    )
    backgroundColor: BackgroundColor = Field(
        default=BackgroundColor.PRIMARY,
        description="Background color of the button",
        optional=True
    )
    textColor: TextColor = Field(
        default=TextColor.PRIMARY_CONTENT,
        description="Text color of the button",
        optional=True
    )
    disabled: bool = Field(
        default=False,
        description="Whether the button is disabled",
        optional=True
    )