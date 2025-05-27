from pydantic import Field

from schemas.ui.page import BaseComponentSchema

class Spacing(BaseComponentSchema):
    """
    Schema for Spacing component
    """
    size: int = Field(..., description="Size of the spacing")