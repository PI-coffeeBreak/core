import logging

import os
from sqlalchemy.orm import Session
from dependencies.mongodb import db
from dependencies.database import get_db

from schemas.ui.menu import Menu, MenuOption
from schemas.ui.color_theme import ColorTheme
from schemas.ui.page import Page

from schemas.ui.components.title import Title
from schemas.ui.components.image import Image
from schemas.ui.components.text import Text
from schemas.ui.components.button import Button
from schemas.ui.components.location import Location
from schemas.ui.components.video import Video
from schemas.ui.components.activities import Activities
from schemas.ui.components.next_activity import NextActivity
from schemas.ui.components.carousel import Carousel
from schemas.ui.components.spacing import Spacing

from services.manifest import ManifestService
from services.component_registry import ComponentRegistry
from services.media import MediaService
from services.favicon import FaviconService

from exceptions.favicon import FaviconNotFoundError
from exceptions.manifest import ManifestNotFoundError

from schemas.favicon import Favicon
from schemas.manifest import Manifest

from constants.mime_types import MimeTypes
from models.media import Media
from repository.media import LocalMediaRepo

logger = logging.getLogger("coffeebreak")

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
MediaService.set_repository(lambda: LocalMediaRepo(MEDIA_ROOT))


async def create_default_test_media(db: Session):
    """Creates a default media entity for testing if it doesn't exist"""
    try:
        # Check if test media already exists
        existing = db.query(Media).filter(Media.alias == 'test-image').first()
        if existing:
            logger.debug(
                f"Test media already exists with UUID: {existing.uuid}")
            return existing

        # Register a media entity that only accepts images
        media = MediaService.register(
            db,
            max_size=5 * 1024 * 1024,  # 5MB
            allows_rewrite=True,
            valid_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            alias='test-image'
        )
        logger.debug(f"Created default test media with UUID: {media.uuid}")
        return media
    except Exception as e:
        logger.error(f"Error creating default test media: {e}")
        return None


async def create_default_main_menu():
    """Creates the default main menu if it doesn't exist"""
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = Menu(options=[
            MenuOption(icon="FaHome", label="Home", href="/home"),
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
            description="Welcome to the home page",
            enabled=True,
            components=[
            ]
        )
        await pages_collection.insert_one(home_page.model_dump())
        logger.debug(f"Created default home page: {home_page}")


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
    component_registry.register_component(Title)
    logger.debug("Registered Title component")
    component_registry.register_component(Image)
    logger.debug("Registered Image component")
    component_registry.register_component(Text)
    logger.debug("Registered Text component")
    component_registry.register_component(Button)
    logger.debug("Registered Button component")
    component_registry.register_component(Location)
    logger.debug("Registered Location component")
    component_registry.register_component(Video)
    logger.debug("Registered Video component")
    component_registry.register_component(Activities)
    logger.debug("Registered Activities component")
    component_registry.register_component(NextActivity)
    logger.debug("Registered NextActivity component")
    component_registry.register_component(Carousel)
    logger.debug("Registered Carousel component")
    component_registry.register_component(Spacing)
    logger.debug("Registered Spacing component")

async def create_default_manifest():
    """Creates the default manifest if it doesn't exist"""
    manifest_service = ManifestService()
    try:
        _manifest = await manifest_service.get_manifest()
    except ManifestNotFoundError:
        default_manifest = Manifest(
            id="/?source=pwa",
            name="coffeeBreak",
            short_name="coffeeBreak",
            description="An app to manage events",
            display="standalone",
            orientation="portrait",
            scope="/",
            start_url="/?source=pwa",
            background_color="#ffffff",
            theme_color="#ffffff",
            icons=[
                {"src": "/pwa-192x192.png", "sizes": "192x192", "type": MimeTypes.PNG, "purpose": "any"},
                {"src": "/pwa-512x512.png", "sizes": "512x512", "type": MimeTypes.PNG, "purpose": "any"},
                {"src": "/pwa-192x192.png", "sizes": "192x192", "type": MimeTypes.PNG, "purpose": "maskable"},
                {"src": "/pwa-512x512.png", "sizes": "512x512", "type": MimeTypes.PNG, "purpose": "maskable"},
            ]
        )
        await manifest_service.update_manifest(default_manifest)

async def create_default_favicon():
    """Creates the default favicon if it doesn't exist"""
    # type="image/svg+xml" href="/vite.svg"
    favicon_service = FaviconService()
    try:
        _favicon = await favicon_service.get_favicon()
    except FaviconNotFoundError:
        default_favicon = Favicon(
            url="/giant_white_bean.svg",
            type=MimeTypes.SVG
        )
        await favicon_service.store_favicon(default_favicon)

async def initialize_defaults():
    """Initialize all default data"""
    logger.info("Initializing default data...")

    # Initialize SQL defaults
    db = next(get_db())
    await create_default_test_media(db)

    # Initialize MongoDB defaults
    await create_default_main_menu()
    await register_default_components()
    await create_default_pages()
    await create_default_color_theme()
    await create_default_manifest()
    await create_default_favicon()
    logger.info("Default data initialization completed")
