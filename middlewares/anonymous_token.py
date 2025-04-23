from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import os

class AnonymousTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response: Response = await call_next(request)

        token = getattr(request.state, "generated_token", None)
        if token:
            response.set_cookie(
                key="anon_token",
                value=token,
                httponly=True,
                secure=os.environ.get("ENVIRONMENT", "development") == "production",
                samesite="Lax",
                max_age=60 * 60 * 24 * 7
            )

        return response 