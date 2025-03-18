from fastapi import FastAPI
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader

from routes import users, activities, activity_types, auth, main_menu
from dependencies.database import engine, Base
from dependencies.mongodb import db
from schemas.ui.main_menu import MainMenu, MenuOption

app = FastAPI()

logger = logging.getLogger("coffeebreak")

plugin_loader('plugins', app)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_default_main_menu()
    yield

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(activity_types.router, prefix="/activity_types", tags=["Activity Types"])
app.include_router(auth.router, tags=["Auth"])

# Include UI routers
app.include_router(main_menu.router, prefix="/ui/menu", tags=["Main Menu"])

# Run with: uvicorn main:app --reload --log-config logging_config.json
# load env file: --env-file <env_file>
