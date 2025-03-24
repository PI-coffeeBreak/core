from fastapi import APIRouter
from typing import List
from schemas.plugin_setting import PluginSetting
from services.ui.plugin_settings import (
    get_plugin_setting_by_title,
    list_plugin_settings
)

router = APIRouter()

@router.get("/{plugin_name}", response_model=PluginSetting)
async def get_plugin_setting_by_name_endpoint(plugin_name: str):
    return await get_plugin_setting_by_title(plugin_name)

@router.get("/", response_model=List[PluginSetting])
async def list_plugin_settings_endpoint():
    return await list_plugin_settings()