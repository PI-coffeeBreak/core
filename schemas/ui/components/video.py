from pydantic import Field
from schemas.ui.page import BaseComponentSchema
from schemas.media import Media
from typing import Optional

class Video(BaseComponentSchema):
    """
    Schema for Video component

    Attributes:
        src (str): The source URL of the video
        autoplay (bool): Whether the video should autoplay
        controls (bool): Whether to show video controls
        loop (bool): Whether the video should loop
        muted (bool): Whether the video should be muted
        poster (str): The URL of the poster image for the video
        allowFullscreen (bool): Whether to allow fullscreen mode
        startAt (int): Time in seconds to start the video at
    """
    src: str | Media = Field(
        ..., description="The source URL of the video (can be an external URL or a Media reference)")
    autoplay: bool = Field(default=False, description="Whether the video should autoplay", optional=True)
    controls: bool = Field(default=True, description="Whether to show video controls", optional=True)
    loop: bool = Field(default=False, description="Whether the video should loop", optional=True)
    muted: bool = Field(default=False, description="Whether the video should be muted", optional=True)
    allowFullscreen: bool = Field(default=True, description="Whether to allow fullscreen mode", optional=True)
    startAt: int = Field(
        default=0,
        description="Time in seconds to start the video at",
        optional=True,
        ge=0
    )
    poster: Optional[str | Media] = Field(
        default=None,
        description="The URL of the poster image for the video (can be an external URL or a Media reference)",
        optional=True
    )