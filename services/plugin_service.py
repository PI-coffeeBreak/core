from typing import Callable, Dict

_settings_callbacks: Dict[str, Callable] = {}

def register_settings_callback(plugin_name: str, callback: Callable):
    _settings_callbacks[plugin_name] = callback

def get_settings_callback(plugin_name: str) -> Callable:
    return _settings_callbacks.get(plugin_name)
