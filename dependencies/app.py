from fastapi import FastAPI

_app: FastAPI = None

def set_current_app(app: FastAPI):
    global _app
    _app = app

def get_current_app() -> FastAPI:
    return _app