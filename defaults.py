import logging
from dependencies.mongodb import db
from schemas.ui.menu import Menu, MenuOption
from schemas.ui.color_theme import ColorTheme
from schemas.ui.page import BaseComponentSchema
from services.ui.page_service import page_service
from services.component_registry import ComponentRegistry

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

async def create_default_pages():
    """Creates the default pages if they don't exist"""
    # Check if the pages collection is empty
    pages_collection = db['pages']
    if await pages_collection.count_documents({}) == 0:
        default_page = {
            "title": "Home",
            "components": [
                {"component_id": "1", "type": "TextComponent", "content": "Welcome to CoffeeBreak!"},
            ]
        }
        activities_page = {
            "title": "Activities",
            "components": [
                {"component_id": "2", "type": "TextComponent", "content": "Activities Page"},
            ]
        }
        profile_page = {
            "title": "Profile",
            "components": [
                {"component_id": "3", "type": "TextComponent", "content": "Profile Page"},
            ]
        }
        await pages_collection.insert_one(default_page)
        await pages_collection.insert_one(activities_page)
        await pages_collection.insert_one(profile_page)
        logger.debug("Default pages created successfully")
    else:
        logger.debug("Default pages already exist")

async def create_default_components():
    """Creates the default components if they don't exist"""
    # Ensure the ComponentRegistry is initialized
    component_registry = ComponentRegistry()
    if not component_registry:
        raise ValueError("Component registry is not initialized")

    # Define the default components
    class TextComponent(BaseComponentSchema):
        name: str
        content: str

    class TitleComponent(BaseComponentSchema):
        name: str
        title: str

    class ImageComponent(BaseComponentSchema):
        name: str
        src: str

    class ButtonComponent(BaseComponentSchema):
        name: str
        label: str
        methods: list = ["GET", "POST", "PUT", "DELETE"]
        url: str

    class RowComponent(BaseComponentSchema):
        name: str
        components: list

    class ColumnComponent(BaseComponentSchema):
        name: str
        components: list

    class CardComponent(BaseComponentSchema):
        name: str
        components: list

    # Register the components
    try:
        component_registry.register_component(TextComponent)
        component_registry.register_component(TitleComponent)
        component_registry.register_component(ImageComponent)
        component_registry.register_component(ButtonComponent)
        component_registry.register_component(RowComponent)
        component_registry.register_component(ColumnComponent)
        component_registry.register_component(CardComponent)
        logger.debug("Default components registered successfully")
    except ValueError as e:
        logger.warning(f"Component registration failed: {str(e)}")

    # Log all available components
    components = component_registry.list_components()
    logger.debug("Available components:")
    for name, component in components.items():
        logger.debug(f"  - {name}: {component.__name__}")
    logger.debug("Default components created successfully")