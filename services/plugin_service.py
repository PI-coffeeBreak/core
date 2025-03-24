from typing import Callable, Dict
from plugin_loader import plugins_modules, registered_plugins

def update_plugin_settings(plugin_name: str, settings: dict) -> bool:
    if plugin_name not in plugins_modules:
        return False
    module = plugins_modules[plugin_name]
    if not hasattr(module, 'SETTINGS'):
        return False
    module.SETTINGS.update(settings)
    return True

def is_plugin_loaded(plugin_name: str) -> bool:
    return plugin_name in registered_plugins
