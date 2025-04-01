from fastapi.openapi.utils import get_openapi

def configure_swagger_ui(app):
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
                "tokenUrl": "/api/v1/token",
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
