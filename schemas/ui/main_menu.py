from pydantic import BaseModel
from typing import List
from .menu import MenuOption

class MainMenu(BaseModel):
    options: List[MenuOption]
    