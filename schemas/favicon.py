from pydantic import BaseModel
from constants.mime_types import MimeTypes

class Favicon(BaseModel):
    url: str
    type: MimeTypes
    