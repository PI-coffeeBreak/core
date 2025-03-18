from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.ui.main_menu import MainMenu, MenuOption
from dependencies.mongodb import db
from dependencies.auth import check_role

router = APIRouter()

main_menu_collection = db['main_menu_collection']

@router.post("/", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def create_main_menu(main_menu: MainMenu):
    if await main_menu_collection.count_documents({}) > 0:
        raise HTTPException(status_code=400, detail="Main menu already exists")
    main_menu_dict = main_menu.model_dump()
    result = await main_menu_collection.insert_one(main_menu_dict)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create main menu")
    return main_menu

@router.get("/", response_model=MainMenu)
async def get_main_menu():
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    return main_menu

@router.put("/", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def update_main_menu(main_menu: MainMenu):
    main_menu_dict = main_menu.model_dump()
    result = await main_menu_collection.update_one({}, {"$set": main_menu_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Main menu not found")
    return main_menu

@router.delete("/", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def delete_main_menu():
    main_menu = await main_menu_collection.find_one_and_delete({})
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    return main_menu

@router.post("/option", response_model=MainMenu, dependencies=[Depends(check_role(["customization"]))])
async def add_menu_option(option: MenuOption):
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    main_menu['options'].append(option.model_dump())
    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add menu option")
    return main_menu

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
    main_menu = await main_menu_collection.find_one()
    if not main_menu:
        raise HTTPException(status_code=404, detail="Main menu not found")
    if option_index >= len(main_menu['options']):
        raise HTTPException(status_code=404, detail="Menu option not found")
    main_menu['options'].pop(option_index)
    result = await main_menu_collection.update_one({}, {"$set": main_menu})
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete menu option")
    return main_menu