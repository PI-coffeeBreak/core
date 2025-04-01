from typing import List, Callable
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from plugin_loader import load_plugin, unload_plugin, plugins_modules
from dependencies.app import get_current_app
from services.plugin_service import update_plugin_settings, get_plugin_details, get_all_plugin_details
from schemas.plugin import PluginAction, PluginSettings, PluginDetails

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


@router.get("/", response_model=List[PluginDetails])
async def list_plugins_endpoint(current_user: dict = Depends(check_role(["manage_plugins"]))):
    return get_all_plugin_details()


@router.get("/{plugin_name}", response_model=PluginDetails)
async def fetch_plugin_endpoint(plugin_name: str, current_user: dict = Depends(check_role(["manage_plugins"]))):
    try:
        return get_plugin_details(plugin_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/submit-settings/{plugin_name}", response_model=dict)
async def submit_settings_endpoint(plugin_name: str, settings: PluginSettings, current_user: dict = Depends(check_role(["manage_plugins"]))):
    if not update_plugin_settings(plugin_name, settings.settings):
        raise HTTPException(status_code=404, detail=f"Plugin {plugin_name} not found or does not have SETTINGS dictionary")
    return {"status": "success", "message": f"Settings for {plugin_name} submitted"}
