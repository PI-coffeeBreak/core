from schemas.ui.menu import MenuOption
from dependencies.mongodb import db
from fastapi import HTTPException


async def create_menu_option(icon: str, label: str, href: str):
    main_menu_collection = db['main_menu_collection']
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")

    new_option = MenuOption(icon=icon, label=label, href=href)
    main_menu['options'].append(new_option.model_dump())

    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to add menu option")

    return main_menu


async def remove_menu_option(option_id: str):
    main_menu_collection = db['main_menu_collection']
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")

    option_index = next((i for i, opt in enumerate(
        main_menu['options']) if opt['id'] == option_id), -1)
    if option_index == -1:
        raise HTTPException(status_code=404, detail="Menu option not found")

    main_menu['options'].pop(option_index)

    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to remove menu option")

    return main_menu
