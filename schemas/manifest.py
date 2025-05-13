from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from constants.mime_types import MimeTypes


class Icon(BaseModel):
    src: str
    sizes: str
    type: MimeTypes
    purpose: Optional[str] = None

class InsertIcon(BaseModel):
    src: str
    sizes: str
    type: MimeTypes

class Manifest(BaseModel):
    id: str
    name: str
    short_name: str
    description: str
    display: str
    orientation: str
    scope: str
    start_url: str
    background_color: str
    theme_color: str
    icons: List[Icon]
