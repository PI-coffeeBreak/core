from pydantic import Field
from schemas.ui.page import BaseComponentSchema


class Location(BaseComponentSchema):
    """
    Schema for Location component

    Attributes:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
        zoom (int): Zoom level for the map
        className (str): CSS classes to be applied
    """
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    address: str = Field(..., description="Address of the location")
    venueTitle: str = Field(..., description="Title of the venue")
    zoom: int = Field(..., description="Zoom level for the map")
    className: str = Field(
        default="",
        description="CSS classes to be applied",
        optional=True
    )
