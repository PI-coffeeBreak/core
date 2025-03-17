from fastapi import FastAPI
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from routes import users, activities, activity_types, auth, main_menu
from dependencies.database import engine, Base

app = FastAPI()

logger = logging.getLogger("coffeebreak")

class CoffeeBreakLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.debug(f"{request.method} {request.url} - {response.status_code}")
        return response

app.add_middleware(CoffeeBreakLoggerMiddleware)

Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(activity_types.router, prefix="/activity_types", tags=["Activity Types"])
app.include_router(auth.router, tags=["Auth"])

# Include UI routers
app.include_router(main_menu.router, prefix="/ui/menu", tags=["Main Menu"])

# Run with: uvicorn main:app --reload --log-config logging_config.json
# load env file: --env-file <env_file>
