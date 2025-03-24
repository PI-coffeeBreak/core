from fastapi import APIRouter
from . import users, activities, activity_types, auth, plugins
from .ui import page, main_menu, plugin_settings

# Create a new APIRouter instance
routes_app = APIRouter()

# Include all routers
routes_app.include_router(users.router, prefix="/users", tags=["Users"])
routes_app.include_router(activities.router, prefix="/activities", tags=["Activities"])
routes_app.include_router(activity_types.router, prefix="/activity-types", tags=["Activity Types"])
routes_app.include_router(auth.router, tags=["Auth"])
routes_app.include_router(page.router, prefix="/pages", tags=["Pages"])
routes_app.include_router(plugins.router, prefix="/plugins", tags=["Plugins"])

# Include UI routers
routes_app.include_router(main_menu.router, prefix="/ui/menu", tags=["Main Menu"])
routes_app.include_router(plugin_settings.router, prefix="/ui/plugin-config", tags=["Plugin Settings"])
