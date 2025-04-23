from fastapi.middleware.cors import CORSMiddleware
from dependencies.app import get_current_app
from .logger import CoffeeBreakLoggerMiddleware
from .anonymous_token import AnonymousTokenMiddleware

__all__ = ['CoffeeBreakLoggerMiddleware', 'AnonymousTokenMiddleware']

# CORS configuration for development environments
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5175"
]

def setup_middlewares():
    app = get_current_app()
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Setup application middlewares
    app.add_middleware(CoffeeBreakLoggerMiddleware)
    app.add_middleware(AnonymousTokenMiddleware) 