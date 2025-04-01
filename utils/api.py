import logging
from typing import Callable, Dict, List
from fastapi import WebSocket, Depends

logger = logging.getLogger("plugin_router")

class Router:
    """A framework-agnostic router that allows plugins to register routes without depending on FastAPI."""

    def __init__(self, prefix: str = ""):
        self.routes: List[Dict] = []
        self.events: Dict[str, Callable] = {}

    def add_route(self, path: str, method: str, handler: Callable, response_model=None):
        """Registers a new route definition."""
        self.routes.append({
            "path": path,
            "method": method.upper(),
            "handler": handler,
            "response_model": response_model
        })
        logger.info(f"Registered route: {method.upper()} {path}")

    def get(self, path: str, response_model=None):
        """Decorator for defining a GET route."""
        def wrapper(handler: Callable):
            self.add_route(path, "GET", handler, response_model)
            return handler
        return wrapper

    def post(self, path: str, response_model=None):
        """Decorator for defining a POST route."""
        def wrapper(handler: Callable):
            self.add_route(path, "POST", handler, response_model)
            return handler
        return wrapper

    def put(self, path: str, response_model=None):
        """Decorator for defining a PUT route."""
        def wrapper(handler: Callable):
            self.add_route(path, "PUT", handler, response_model)
            return handler
        return wrapper

    def delete(self, path: str, response_model=None):
        """Decorator for defining a DELETE route."""
        def wrapper(handler: Callable):
            self.add_route(path, "DELETE", handler, response_model)
            return handler
        return wrapper

    def patch(self, path: str, response_model=None):
        """Decorator for defining a PATCH route."""
        def wrapper(handler: Callable):
            self.add_route(path, "PATCH", handler, response_model)
            return handler
        return wrapper

    def options(self, path: str):
        """Decorator for defining an OPTIONS route."""
        def wrapper(handler: Callable):
            self.add_route(path, "OPTIONS", handler)
            return handler
        return wrapper

    def head(self, path: str):
        """Decorator for defining a HEAD route."""
        def wrapper(handler: Callable):
            self.add_route(path, "HEAD", handler)
            return handler
        return wrapper

    def trace(self, path: str):
        """Decorator for defining a TRACE route."""
        def wrapper(handler: Callable):
            self.add_route(path, "TRACE", handler)
            return handler
        return wrapper

    def websocket(self, path: str):
        """Decorator for defining a WebSocket route."""
        def wrapper(handler: Callable):
            self.add_route(path, "WEBSOCKET", handler)
            return handler
        return wrapper

    def on_event(self, event: str):
        """Decorator for defining an event handler (e.g., startup, shutdown)."""
        if event not in ["startup", "shutdown"]:
            raise ValueError("Event must be either 'startup' or 'shutdown'.")
        def wrapper(handler: Callable):
            self.events[event] = handler
            return handler
        return wrapper

    def include_router(self, router, prefix: str):
        for route in router.routes:
            route["path"] = f"{prefix}{route['path']}"
            self.routes.append(route)
            logger.info(f"Included route: {route['method']} {route['path']}")

    def get_router(self):
        """Registers the stored routes into FastAPI if it's available."""
        try:
            from fastapi import APIRouter

            router = APIRouter()
            for route in self.routes:
                if route["method"] == "GET":
                    router.get(route["path"], response_model=route["response_model"])(route["handler"])
                elif route["method"] == "POST":
                    router.post(route["path"], response_model=route["response_model"])(route["handler"])
                elif route["method"] == "PUT":
                    router.put(route["path"], response_model=route["response_model"])(route["handler"])
                elif route["method"] == "DELETE":
                    router.delete(route["path"], response_model=route["response_model"])(route["handler"])
                elif route["method"] == "PATCH":
                    router.patch(route["path"], response_model=route["response_model"])(route["handler"])
                elif route["method"] == "OPTIONS":
                    router.options(route["path"])(route["handler"])
                elif route["method"] == "HEAD":
                    router.head(route["path"])(route["handler"])
                elif route["method"] == "TRACE":
                    router.trace(route["path"])(route["handler"])
                elif route["method"] == "WEBSOCKET":
                    router.websocket(route["path"])(route["handler"])

            for event, handler in self.events.items():
                router.on_event(event)(handler)

            return router
        except ImportError:
            logger.warning("FastAPI is not installed. Routes will not be registered.")
            return None

    def __str__(self):
        return f"Router(routes={self.routes})"