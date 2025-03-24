from typing import List, Callable
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import get_current_user, check_role
from services.user_service import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user
)
from plugin_loader import load_plugin, unload_plugin, plugins_modules
from dependencies.app import get_current_app
from services.plugin_service import update_plugin_settings, is_plugin_loaded
from schemas.plugin import PluginAction, PluginSettings

router = APIRouter()


@router.post("/load", response_model=dict)
async def load_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app), current_user: dict = Depends(check_role(["manage_plugins"]))):
    if not load_plugin(app, action.plugin_name):
        raise HTTPException(
            status_code=400, detail=f"Plugin {action.plugin_name} is not an unloaded plugin")
    return {"status": "success", "message": f"Plugin {action.plugin_name} loaded"}


@router.post("/unload", response_model=dict)
async def unload_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app), current_user: dict = Depends(check_role(["manage_plugins"]))):
    if not unload_plugin(app, action.plugin_name):
        raise HTTPException(
            status_code=400, detail=f"Plugin {action.plugin_name} is not a loaded plugin")
    return {"status": "success", "message": f"Plugin {action.plugin_name} unloaded"}


@router.get("/", response_model=List[str])
async def list_plugins_endpoint(current_user: dict = Depends(check_role(["manage_plugins"]))):
    return list(plugins_modules.keys())


@router.get("/{plugin_name}", response_model=dict)
async def fetch_plugin_endpoint(plugin_name: str, current_user: dict = Depends(check_role(["manage_plugins"]))):
    if plugin_name in plugins_modules:
        module = plugins_modules[plugin_name]
        details = {
            "name": plugin_name,
            "has_register": hasattr(module, 'REGISTER'),
            "has_unregister": hasattr(module, 'UNREGISTER'),
            "has_router": hasattr(module, 'router'),
            "is_loaded": is_plugin_loaded(plugin_name)
        }
        return details
    else:
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not found")


@router.post("/submit-settings/{plugin_name}", response_model=dict)
async def submit_settings_endpoint(plugin_name: str, settings: PluginSettings, current_user: dict = Depends(check_role(["manage_plugins"]))):
    if not update_plugin_settings(plugin_name, settings.settings):
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not found or does not have SETTINGS dictionary")
    return {"status": "success", "message": f"Settings for {plugin_name} submitted"}
