from typing import Callable, Dict
from plugin_loader import plugins_modules, registered_plugins
from schemas.plugin import PluginDetails
from exceptions.plugin import (
    PluginNotFoundError,
    PluginSettingsError
)

def update_plugin_settings(plugin_name: str, settings: dict) -> None:
    if plugin_name not in plugins_modules:
        raise PluginNotFoundError(plugin_name)
    module = plugins_modules[plugin_name]
    if not hasattr(module, 'SETTINGS'):
        raise PluginSettingsError(plugin_name)
    module.SETTINGS.update(settings)

def is_plugin_loaded(plugin_name: str) -> bool:
    return plugin_name in registered_plugins

def get_plugin_details(plugin_name: str) -> PluginDetails:
    if plugin_name not in plugins_modules:
        raise PluginNotFoundError(plugin_name)
    module = plugins_modules[plugin_name]
    return PluginDetails(
        name=plugin_name,
        has_register=hasattr(module, 'REGISTER'),
        has_unregister=hasattr(module, 'UNREGISTER'),
        has_router=hasattr(module, 'router'),
        is_loaded=is_plugin_loaded(plugin_name),
        description=getattr(module, 'DESCRIPTION', "No description provided")
    )

def get_all_plugin_details() -> list[PluginDetails]:
    plugin_details = []
    for plugin_name in plugins_modules.keys():
        plugin_details.append(get_plugin_details(plugin_name))
    return plugin_details
