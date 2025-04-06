from pydantic import BaseModel, Field
from schemas.ui.page import BaseComponentSchema


class ButtonComponent(BaseComponentSchema):
    """
    Schema for Button component

    Attributes:
        text (str): The text to be displayed on the button
        METHOD (str): The HTTP method to be used
        URL (str): The URL to be called when the button is clicked
    """
    text: str = Field(...,
                      description="The text to be displayed on the button")
    METHOD: str = Field(..., description="The HTTP method to be used")
    URL: str = Field(...,
                     description="The URL to be called when the button is clicked")
