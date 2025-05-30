from typing import List, Callable, Dict, Any
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import check_role
from plugin_loader import load_plugin, unload_plugin, plugins_modules
from dependencies.app import get_current_app
from services.plugin_service import update_plugin_settings, get_plugin_details, get_all_plugin_details, get_plugin_settings
from schemas.plugin import PluginAction, PluginSettings, PluginDetails
from exceptions.plugin import PluginError, PluginNotFoundError, PluginSettingsError
router = APIRouter()


@router.post("/load", response_model=dict)
async def load_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app), current_user: dict = Depends(check_role(["manage_plugins"]))):
    try:
        await load_plugin(app, action.plugin_name)
        return {"status": "success", "message": f"Plugin {action.plugin_name} loaded"}
    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/unload", response_model=dict)
async def unload_plugin_endpoint(action: PluginAction, app: FastAPI = Depends(get_current_app), current_user: dict = Depends(check_role(["manage_plugins"]))):
    try:
        await unload_plugin(app, action.plugin_name)
        return {"status": "success", "message": f"Plugin {action.plugin_name} unloaded"}
    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/", response_model=List[PluginDetails])
async def list_plugins_endpoint(current_user: dict = Depends(check_role(["manage_plugins"]))):
    return get_all_plugin_details()


@router.get("/{plugin_name}", response_model=PluginDetails)
async def fetch_plugin_endpoint(plugin_name: str, current_user: dict = Depends(check_role(["manage_plugins"]))):
    try:
        return get_plugin_details(plugin_name)
    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.post("/submit-settings/{plugin_name}", response_model=dict)
async def submit_settings_endpoint(plugin_name: str, settings: PluginSettings, current_user: dict = Depends(check_role(["manage_plugins"]))):
    try:
        result = update_plugin_settings(plugin_name, settings.settings)
        return {"status": "success", "message": f"Settings for {plugin_name} submitted", "settings": result}
    except PluginError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/settings/{plugin_name}", response_model=Dict[str, Any])
async def get_plugin_settings_endpoint(plugin_name: str, current_user: dict = Depends(check_role(["manage_plugins"]))):
    """
    Get the current settings for a plugin
    """
    try:
        settings = get_plugin_settings(plugin_name)
        return settings
    except PluginNotFoundError:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
    except PluginSettingsError:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' has no settings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving settings: {str(e)}")
