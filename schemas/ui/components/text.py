from pydantic import BaseModel, Field
from schemas.ui.page import BaseComponentSchema


class TextComponent(BaseComponentSchema):
    """
    Schema for Text component

    Attributes:
        content (str): The text content to be displayed
    """
    content: str = Field(..., description="The text content to be displayed")
