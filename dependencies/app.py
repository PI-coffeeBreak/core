from typing import Optional
from fastapi import FastAPI

_app: Optional[FastAPI] = None

def set_current_app(app: FastAPI):
    global _app
    _app = app

def get_current_app() -> FastAPI:
    if _app is None:
        raise RuntimeError("The FastAPI app has not been set.")
    return _app