from fastapi import Request
from dependencies.app import get_current_app
import logging

logger = logging.getLogger("coffeebreak")

@get_current_app().middleware("http")
async def dispatch(request: Request, call_next):
    response = await call_next(request)
    logger.debug(f"{request.method} {request.url} - {response.status_code}")
    return response 