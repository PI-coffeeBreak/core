from typing import List
from fastapi import HTTPException
from schemas.plugin_setting import PluginSetting
from dependencies.mongodb import db

plugin_settings_collection = db['plugin_settings']

async def list_plugin_settings() -> List[PluginSetting]:
    plugin_settings = await plugin_settings_collection.find().to_list(None)
    return [PluginSetting(**plugin_setting) for plugin_setting in plugin_settings]

async def create_plugin_setting(plugin_setting: PluginSetting) -> PluginSetting:
    result = await plugin_settings_collection.insert_one(plugin_setting.model_dump())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create plugin setting")
    return plugin_setting

async def get_plugin_setting_by_title(plugin_title: str) -> PluginSetting:
    plugin_setting = await plugin_settings_collection.find_one({"title": plugin_title})
    if not plugin_setting:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    return PluginSetting(**plugin_setting)

async def update_plugin_setting_by_title(plugin_title: str, plugin_setting: PluginSetting) -> PluginSetting:
    result = await plugin_settings_collection.update_one(
        {"title": plugin_title},
        {"$set": plugin_setting.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update plugin setting")
    return plugin_setting

async def delete_plugin_setting_by_title(plugin_title: str) -> PluginSetting:
    plugin_setting = await plugin_settings_collection.find_one({"title": plugin_title})
    if not plugin_setting:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    result = await plugin_settings_collection.delete_one({"title": plugin_title})
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete plugin setting")
    return PluginSetting(**plugin_setting)
