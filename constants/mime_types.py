from enum import Enum

class MimeTypes(str, Enum):
    """Common MIME types used in the application"""
    PNG = "image/png" 
    JPEG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    WEBM = "video/webm"
    MP4 = "video/mp4"
    OGG = "video/ogg"
