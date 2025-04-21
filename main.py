from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager
from plugin_loader import plugin_loader
from dependencies.app import set_current_app

from dependencies.database import engine, Base
from swagger import configure_swagger_ui
from plugin_loader import plugin_unloader
from defaults import initialize_defaults
from services.message_bus import MessageBus
from services.notifications import NotificationService
from services.handlers import register_notification_handlers
from dependencies.database import get_db

logger = logging.getLogger("coffeebreak")

app = FastAPI(root_path="/api/v1", openapi_prefix="/api/v1")
set_current_app(app)

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
        # Get database session
        db = next(get_db())

        # Initialize services
        message_bus = MessageBus(db)
        notification_service = NotificationService(db)

        # Register handlers
        await register_notification_handlers(message_bus, notification_service)

        logger.info("Application startup completed successfully")
        yield
    finally:
        await plugin_unloader(routes_app)


app.router.lifespan_context = lifespan

# CORS configuration for development environments
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5175"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CoffeeBreakLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.debug(
            f"{request.method} {request.url} - {response.status_code}")
        return response


app.add_middleware(CoffeeBreakLoggerMiddleware)

# Start the application with:
# uvicorn main:app --reload --log-config logging_config.json
# Additional configuration:
# --env-file <env_file>
