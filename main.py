from fastapi import FastAPI, Request, Response
import logging
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader
from dependencies.app import set_current_app
from dependencies.database import engine, Base, get_db
from swagger import configure_swagger_ui
from plugin_loader import plugin_unloader
from defaults import initialize_defaults
from services.message_bus import MessageBus
from services.notifications import NotificationService
from middlewares import setup_middlewares
import os

logger = logging.getLogger("coffeebreak")

app = FastAPI(root_path="/api/v1", openapi_prefix="/api/v1")
set_current_app(app)

# Setup middlewares
setup_middlewares()

from routes import routes_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all plugins first
    await plugin_loader('plugins', routes_app)

    # Create database tables after plugins are loaded
    Base.metadata.create_all(bind=engine)

    # Include all routers from routes/__init__.py after plugins
    app.include_router(routes_app)

    # Configure Swagger UI after all routes are registered
    configure_swagger_ui(app)

    # Initialize default configurations
    await initialize_defaults()

    # Log all available routes
    for route in routes_app.routes:
        logger.debug(
            f"Route: {route.path} [{route.methods if hasattr(route, 'methods') else 'WebSocket'}]")

    try:
        yield
    finally:
        await plugin_unloader(routes_app)


app.router.lifespan_context = lifespan

# Start the application with:
# uvicorn main:app --reload --log-config logging_config.json
# Additional configuration:
# --env-file <env_file>
