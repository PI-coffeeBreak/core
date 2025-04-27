from fastapi import HTTPException, status
from constants.errors import PluginErrors

class PluginError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class PluginNotFoundError(PluginError):
    def __init__(self, plugin_name: str):
        super().__init__(PluginErrors.NOT_FOUND.format(plugin_name=plugin_name), 404)

class PluginNotLoadedError(PluginError):
    def __init__(self, plugin_name: str):
        super().__init__(PluginErrors.NOT_LOADED.format(plugin_name=plugin_name), 400)

class PluginSettingsError(PluginError):
    def __init__(self, plugin_name: str):
        super().__init__(PluginErrors.SETTINGS_ERROR.format(plugin_name=plugin_name), 400) 