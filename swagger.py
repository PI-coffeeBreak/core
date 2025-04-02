from fastapi.openapi.utils import get_openapi
import os

# Get the API prefix from the environment variables
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")  # Default to "/api/v1" if not set

def configure_swagger_ui(app):
    app.openapi_url = f"{API_PREFIX}/openapi.json"
    app.openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API documentation",
        routes=app.routes,
    )
    app.openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": f"{API_PREFIX}/token",
                "scopes": {},
            }
        },
    }
    app.openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi = lambda: app.openapi_schema

    # Configure Swagger UI to persist tokens
    app.swagger_ui_init_oauth = {
        "usePkceWithAuthorizationCodeGrant": True,
        "persistAuthorization": True,
    }
