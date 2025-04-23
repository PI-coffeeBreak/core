from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("coffeebreak")

class CoffeeBreakLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.debug(
            f"{request.method} {request.url} - {response.status_code}")
        return response 