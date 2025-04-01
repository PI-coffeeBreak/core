from pydantic import BaseModel
from typing import List

class MenuOption(BaseModel):
    icon: str
    label: str
    href: str

class Menu(BaseModel):
    options: List[MenuOption]




# usage example
if __name__ == "__main__":
    from dependencies.mongodb import db
    # MongoDB connection setup
    menu_collection = db['menu_collection']

    # Example function to insert a menu into the collection
    def insert_menu(menu: Menu):
        menu_collection.insert_one(menu.model_dump())

    # call method

    insert_menu(Menu(options=[
        MenuOption(icon="home", label="Home", href="https://www.example.com"),
        MenuOption(icon="settings", label="Settings", href="https://www.example.com"),
        MenuOption(icon="logout", label="Logout", href="https://www.example.com")
    ]))
