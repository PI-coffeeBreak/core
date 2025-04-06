import logging
from dependencies.mongodb import db
from schemas.ui.menu import Menu, MenuOption
from schemas.ui.color_theme import ColorTheme
from schemas.ui.page import Page
from schemas.ui.components.title import TitleComponent
from schemas.ui.components.image import ImageComponent
from schemas.ui.components.text import TextComponent
from schemas.ui.components.button import ButtonComponent
from services.ui.page_service import page_service
from services.component_registry import ComponentRegistry

logger = logging.getLogger("coffeebreak")


async def create_default_main_menu():
    """Creates the default main menu if it doesn't exist"""
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = Menu(options=[
            MenuOption(icon="FaHome", label="Home", href="/home"),
            MenuOption(icon="FaUser", label="Profile", href="/profile"),
            MenuOption(icon="FaBook", label="Activity", href="/activity"),
        ])
        await main_menu_collection.insert_one(default_main_menu.model_dump())

    # Log all available pages from the menu
    menu = await main_menu_collection.find_one()
    if menu:
        logger.debug("Available pages in main menu:")
        for option in menu['options']:
            logger.debug(
                f"  - {option['label']}: {option['href']} ({option['icon']})")


async def create_default_pages():
    """Creates default pages if they don't exist"""
    pages_collection = db['pages']
    if await pages_collection.count_documents({}) == 0:
        # Create home page with Welcome component
        home_page = Page(
            title="Home",
            components=[
                {
                    "name": "Welcome"
                }
            ]
        )
        await pages_collection.insert_one(home_page.model_dump())
        logger.debug(f"Created default home page: {home_page}")

        # Create profile page with UserProfile component
        profile_page = Page(
            title="Profile",
            components=[
                {
                    "name": "User Profile"
                }
            ]
        )
        await pages_collection.insert_one(profile_page.model_dump())
        logger.debug(f"Created default profile page: {profile_page}")

        # Create activity page with multiple components
        title_component = TitleComponent(
            name="Title",
            text="Activity about AI"
        )

        image_component = ImageComponent(
            name="Image",
            src="",
            alt="Activity Image"
        )

        text_component = TextComponent(
            name="Text",
            content="This is a page for activities. skfl df jf kdf ddfh d jkfsj fdshf dj fds jdfh kjfhdsjkhf sh fjds jkh hjk dj dkj sjkf jskd dh fdsjk fkjsh sdh sjk kfsj hkjsdh fkshh fds fhdfsjfkfdhf fsdjhf sjhf dj ksdhsjd kjh fdfhkjjhfdskjf d jfdsjf dsjf jfkkdh sjfh jhf shhf jsh jsf hsjfh jkd jh jshh kjdshjsh fkshf sjkd fkshh jdh fks sj skh fjs sh jks ksdh fjksd jshh fkjhf sjdh shf js kj dhs fkjf hf sdkj kjs dfh"
        )

        button_component = ButtonComponent(
            name="Button",
            text="Start Activity",
            METHOD="GET",
            URL="https://jsonplaceholder.typicode.com/posts/1"
        )

        activity_page = Page(
            title="Activity",
            components=[
                title_component.model_dump(),
                image_component.model_dump(),
                text_component.model_dump(),
                button_component.model_dump()
            ]
        )
        await pages_collection.insert_one(activity_page.model_dump())
        logger.debug(f"Created default activity page: {activity_page}")


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

async def register_default_components():
    """Register default components"""
    component_registry = ComponentRegistry()
    component_registry.register_component(TitleComponent)
    component_registry.register_component(ImageComponent)
    component_registry.register_component(TextComponent)
    component_registry.register_component(ButtonComponent)


async def initialize_defaults():
    """Initialize all default data"""
    logger.info("Initializing default data...")
    await create_default_main_menu()
    await create_default_pages()
    await create_default_color_theme()
    await register_default_components()
    logger.info("Default data initialization completed")
