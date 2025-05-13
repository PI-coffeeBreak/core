from fastapi import Request, Response
from typing import Callable
import os
from dependencies.app import get_current_app
from constants.anonymous_token import ANONYMOUS_TOKEN_MAX_AGE

@get_current_app().middleware("http")
async def dispatch(request: Request, call_next: Callable):
    response: Response = await call_next(request)

    token = getattr(request.state, "generated_token", None)
    if token:
        response.set_cookie(
            key="anon_token",
            value=token,
            httponly=True,
            secure=os.environ.get("ENVIRONMENT", "development") == "production",
            samesite="Lax",
            max_age=ANONYMOUS_TOKEN_MAX_AGE
        )

    return response 