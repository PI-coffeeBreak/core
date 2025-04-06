import logging
from dependencies.mongodb import db
from schemas.ui.menu import Menu, MenuOption
from schemas.ui.color_theme import ColorTheme
from services.ui.page_service import page_service

logger = logging.getLogger("coffeebreak")


async def create_default_main_menu():
    """Creates the default main menu if it doesn't exist"""
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = Menu(options=[
            MenuOption(icon="home", label="Home", href="/home"),
            MenuOption(icon="profile", label="Profile", href="/profile"),
        ])
        await main_menu_collection.insert_one(default_main_menu.model_dump())

    # Log all available pages from the menu
    menu = await main_menu_collection.find_one()
    if menu:
        logger.debug("Available pages in main menu:")
        for option in menu['options']:
            logger.debug(
                f"  - {option['label']}: {option['href']} ({option['icon']})")


async def create_default_color_theme():
    """Creates the default color theme if it doesn't exist"""
    color_themes_collection = db['color_themes']
    if await color_themes_collection.count_documents({}) == 0:
        default_color_theme = ColorTheme(
            base_100="#f3faff",
            base_200="#d6d6d3",
            base_300="#d6d6d3",
            base_content="#726d65",
            primary="#4f2b1d",
            primary_content="#f3faff",
            secondary="#c6baa2",
            secondary_content="#f1fbfb",
            accent="#faa275",
            accent_content="#f3fbf6",
            neutral="#caa751",
            neutral_content="#f3faff",
            info="#00b2dd",
            info_content="#f2fafd",
            success="#0cae00",
            success_content="#f5faf4",
            warning="#fbad00",
            warning_content="#221300",
            error="#ff1300",
            error_content="#fff6f4",
        )
        await color_themes_collection.insert_one(default_color_theme.model_dump())
