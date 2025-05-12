from pydantic import BaseModel

class Favicon(BaseModel):
    url: str
    