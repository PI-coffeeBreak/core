from fastapi.openapi.utils import get_openapi


def configure_swagger_ui(app):
    """Configure Swagger UI with persistent authentication and better UI"""
    app.openapi_schema = get_openapi(
        title="CoffeeBreak. - API v1",
        version="0.1.0",
        description="""
        API documentation for CoffeeBreak.
        
        ## Authentication
        1. Click on the 'Authorize' button at the top
        2. Use your username and password to get access
        3. Your session will be preserved between page reloads
        """,
        routes=app.routes,
    )

    # Configure API server
    app.openapi_schema["servers"] = [
        {"url": "/api/v1", "description": "Main API server"}
    ]

    # Configure security schemes
    app.openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/token",
                    "scopes": {},
                }
            },
        }
    }

    # Add security requirement to all endpoints by default
    app.openapi_schema["security"] = [
        {"OAuth2PasswordBearer": []}
    ]

    app.openapi = lambda: app.openapi_schema

    # Configure Swagger UI initialization
    app.swagger_ui_init_oauth = {
        "usePkceWithAuthorizationCodeGrant": True,
        "persistAuthorization": True,
        "clientId": "swagger-ui",
    }

    # Configure Swagger UI parameters
    app.swagger_ui_parameters = {
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "tryItOutEnabled": True,
    }
