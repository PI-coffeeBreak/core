from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader
from dependencies.app import set_current_app

from dependencies.database import engine, Base
from dependencies.mongodb import db
from schemas.ui.main_menu import MainMenu, MenuOption
from schemas.ui.color_theme import ColorTheme
from routes import routes_app
from swagger import configure_swagger_ui
from plugin_loader import plugin_unloader

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_default_main_menu()
    await create_default_color_theme()
    configure_swagger_ui(app)
    try:
        yield
    finally:
        await plugin_unloader(routes_app)
        pass

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("coffeebreak")

class CoffeeBreakLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.debug(f"{request.method} {request.url} - {response.status_code}")
        return response

app.add_middleware(CoffeeBreakLoggerMiddleware)

# Create default main menu if it does not exist
async def create_default_main_menu():
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = MainMenu(options=[
            MenuOption(icon="home", label="Home", href="/home"),
            MenuOption(icon="profile", label="Profile", href="/profile"),
        ])
        await main_menu_collection.insert_one(default_main_menu.model_dump())

# Create default color theme if it does not exist
async def create_default_color_theme():
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

set_current_app(routes_app)
plugin_loader('plugins', routes_app)

Base.metadata.create_all(bind=engine) # should only be called after all plugins being loaded

# Include all routers from routes/__init__.py
app.include_router(routes_app, prefix="/api/v1")

# Run with: uvicorn main:app --reload --log-config logging_config.json
# load env file: --env-file <env_file>
