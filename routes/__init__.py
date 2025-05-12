from fastapi import APIRouter
# All routers should be imported here, otherwise they will not be included in the API
from . import users, activities, activity_types, auth, plugins, totp, notifications, media, event_info, health, websocket, favicon
from .ui import color_themes, page, main_menu, plugin_settings
from .components import router as components_router

# Create a new APIRouter instance
routes_app = APIRouter()

# Include all routers
routes_app.include_router(health.router, prefix="/health", tags=["Health"])
routes_app.include_router(event_info.router,
                          prefix="/event-info", tags=["Event Information"])
routes_app.include_router(users.router, prefix="/users", tags=["Users"])
routes_app.include_router(
    activities.router, prefix="/activities", tags=["Activities"])
routes_app.include_router(activity_types.router,
                          prefix="/activity-types", tags=["Activity Types"])
routes_app.include_router(auth.router, tags=["Auth"])
routes_app.include_router(page.router, prefix="/pages", tags=["Pages"])
routes_app.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])
routes_app.include_router(totp.router, prefix="/totp", tags=["TOTP"])
routes_app.include_router(notifications.router,
                          prefix="/notifications", tags=["Notifications"])
routes_app.include_router(media.router, prefix="/media", tags=["Media"])
routes_app.include_router(favicon.router, prefix="/favicon", tags=["Favicon"])

# Include UI routers
routes_app.include_router(main_menu.router, prefix="/ui/menu", tags=["UI"])
routes_app.include_router(plugin_settings.router,
                          prefix="/ui/plugin-config", tags=["Plugin Settings"])
routes_app.include_router(
    color_themes.router, prefix="/ui/color-theme", tags=["Color Theme"])
routes_app.include_router(websocket.router, tags=["WebSocket"])

# Include component registry router
routes_app.include_router(
    components_router, prefix="/components", tags=["Components"])
