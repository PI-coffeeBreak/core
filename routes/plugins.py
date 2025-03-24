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
from services.plugin_service import register_settings_callback, get_settings_callback
from schemas.plugin import PluginAction, PluginSettings

router = APIRouter()


@router.post("/load", response_model=dict)
async def load_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app)):
    if not load_plugin(app, action.plugin_name):
        raise HTTPException(
            status_code=400, detail=f"Plugin {action.plugin_name} is not an unloaded plugin")
    return {"status": "success", "message": f"Plugin {action.plugin_name} loaded"}


@router.post("/unload", response_model=dict)
async def unload_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app)):
    if not unload_plugin(app, action.plugin_name):
        raise HTTPException(
            status_code=400, detail=f"Plugin {action.plugin_name} is not a loaded plugin")
    return {"status": "success", "message": f"Plugin {action.plugin_name} unloaded"}


@router.get("/", response_model=List[str])
async def list_plugins_endpoint():
    return list(plugins_modules.keys())


@router.get("/{plugin_name}", response_model=dict)
async def fetch_plugin_endpoint(plugin_name: str):
    if (plugin_name in plugins_modules):
        module = plugins_modules[plugin_name]
        details = {
            "name": plugin_name,
            "has_register": hasattr(module, 'REGISTER'),
            "has_unregister": hasattr(module, 'UNREGISTER'),
            "has_router": hasattr(module, 'router')
        }
        return details
    else:
        raise HTTPException(
            status_code=404, detail=f"Plugin {plugin_name} not found")


@router.post("/submit-settings/{plugin_name}", response_model=dict)
async def submit_settings_endpoint(plugin_name: str, settings: PluginSettings):
    callback = get_settings_callback(plugin_name)
    if not callback:
        raise HTTPException(
            status_code=404, detail=f"No callback registered for {plugin_name}")
    try:
        callback(settings.settings)
        return {"status": "success", "message": f"Settings for {plugin_name} submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
