from pydantic import BaseModel, Field
from schemas.ui.page import BaseComponentSchema


class TitleComponent(BaseComponentSchema):
    """
    Schema for Title component

    Attributes:
        text (str): The text to be displayed
        className (str): CSS classes to be applied
    """
    text: str = Field(..., description="The text to be displayed")
