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
    latitude: float = Field(default=40.62338, description="Latitude of the location")
    longitude: float = Field(default=-8.65784, description="Longitude of the location")
    address: str = Field(... , description="Address of the location")
    venueTitle: str = Field(... , description="Title of the venue")
    zoom: int = Field(default=12, description="Zoom level for the map")
