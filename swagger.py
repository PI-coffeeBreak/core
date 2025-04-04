from fastapi.openapi.utils import get_openapi

def configure_swagger_ui(app):
    app.openapi_schema = get_openapi(
        title="CoffeeBreak. - API v1",
        version="0.1.0",
        description="API documentation",
        routes=app.routes,
    )
    app.openapi_schema["servers"] = [
        {"url": "/api/v1"}
    ]
    app.openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "/api/v1/token",
                "scopes": {},
            }
        },
    }
    app.openapi = lambda: app.openapi_schema

    # Configure Swagger UI to persist tokens
    app.swagger_ui_init_oauth = {
        "usePkceWithAuthorizationCodeGrant": True,
        "persistAuthorization": True,
    }
