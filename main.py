from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader
from dependencies.app import set_current_app
from dependencies.database import engine, Base
from dependencies.mongodb import db
from schemas.ui.main_menu import MainMenu, MenuOption
from routes import routes_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_default_main_menu()
    yield

app = FastAPI(lifespan=lifespan)

set_current_app(app)

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

Base.metadata.create_all(bind=engine)

# Create default main menu if it does not exist
async def create_default_main_menu():
    main_menu_collection = db['main_menu_collection']
    if await main_menu_collection.count_documents({}) == 0:
        default_main_menu = MainMenu(options=[
            MenuOption(icon="home", label="Home", href="/home"),
            MenuOption(icon="profile", label="Profile", href="/profile"),
        ])
        await main_menu_collection.insert_one(default_main_menu.model_dump())

plugin_loader('plugins', app)

# Include all routers from routes/__init__.py
app.include_router(routes_app, prefix="/api/v1")

# Run with: uvicorn main:app --reload --log-config logging_config.json
# load env file: --env-file <env_file>
