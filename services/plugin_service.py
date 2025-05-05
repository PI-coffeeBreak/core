from typing import Callable, Dict
from plugin_loader import plugins_modules, registered_plugins
from schemas.plugin import PluginDetails
from exceptions.plugin import (
    PluginNotFoundError,
    PluginSettingsError
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

def update_plugin_settings(plugin_name: str, form_data: dict) -> dict:
    """Update a plugin's settings with form data"""
    if plugin_name not in plugins_modules:
        raise PluginNotFoundError(plugin_name)
        
    module = plugins_modules[plugin_name]
    
    if not hasattr(module, 'SETTINGS'):
        raise PluginSettingsError(plugin_name)
    
    # Get existing settings object
    settings = module.SETTINGS
    
    # Get plugin inputs to map form field names to settings fields
    plugin_inputs = getattr(module, 'plugin_inputs', [])
    
    # Create a mapping from form field names to settings field names
    name_to_field = {}
    for inp in plugin_inputs:
        if hasattr(inp, 'name') and inp.name:
            name_to_field[inp.name] = inp.name
    
    # For Pydantic BaseModel settings
    if isinstance(settings, BaseModel):
        settings_dict = {}
        
        # Extract fields that exist in the model
        for field_name in settings.model_fields.keys():
            # Check for direct match or mapped match
            if field_name in form_data:
                settings_dict[field_name] = form_data[field_name]
            elif field_name in name_to_field and name_to_field[field_name] in form_data:
                settings_dict[field_name] = form_data[name_to_field[field_name]]
        
        # Update the model with new values
        for key, value in settings_dict.items():
            setattr(settings, key, value)
            
        logger.info(f"Updated settings for plugin '{plugin_name}': {settings_dict}")
        return settings_dict
    
    # For dictionary settings
    module.SETTINGS.update(form_data)
    logger.info(f"Updated settings for plugin '{plugin_name}': {form_data}")
    return form_data  # Return the form data

def is_plugin_loaded(plugin_name: str) -> bool:
    return plugin_name in registered_plugins

def get_plugin_details(plugin_name: str) -> PluginDetails:
    if plugin_name not in plugins_modules:
        raise PluginNotFoundError(plugin_name)
    module = plugins_modules[plugin_name]
    return PluginDetails(
        name=getattr(module, 'NAME', plugin_name),
        has_register=hasattr(module, 'REGISTER'),
        has_unregister=hasattr(module, 'UNREGISTER'),
        has_router=hasattr(module, 'router'),
        is_loaded=is_plugin_loaded(plugin_name),
        description=getattr(module, 'DESCRIPTION', "No description provided"),
        config_page=getattr(module, 'CONFIG_PAGE', False),
    )

def get_all_plugin_details() -> list[PluginDetails]:
    plugin_details = []
    for plugin_name in plugins_modules.keys():
        plugin_details.append(get_plugin_details(plugin_name))
    return plugin_details
