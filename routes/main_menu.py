from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.ui.main_menu import MainMenu, MenuOption
from dependencies.mongodb import db
from dependencies.auth import check_role
from services.ui.main_menu import create_menu_option, remove_menu_option

router = APIRouter()

main_menu_collection = db['main_menu_collection']

@router.get("/", response_model=MainMenu)
async def get_main_menu():
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    return main_menu

@router.post("/option", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def add_menu_option(option: MenuOption):
    return await create_menu_option(option.icon, option.label, option.href)

@router.put("/option/{option_index}", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def update_menu_option(option_index: int, option: MenuOption):
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    if option_index >= len(main_menu['options']):
        raise HTTPException(status_code=404, detail="Menu option not found")
    main_menu['options'][option_index] = option.model_dump()
    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update menu option")
    return main_menu

@router.delete("/option/{option_index}", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def delete_menu_option(option_index: int):
    return await remove_menu_option(option_index)

@router.put("/options", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def update_menu_options(options: List[MenuOption]):
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    main_menu['options'] = [option.dict() for option in options]
    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update menu options")
    return main_menu