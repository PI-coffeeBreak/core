from pydantic import BaseModel

class PluginAction(BaseModel):
    plugin_name: str

class PluginSettings(BaseModel):
    settings: dict

class PluginDetails(BaseModel):
    name: str
    has_register: bool
    has_unregister: bool
    has_router: bool
    is_loaded: bool
    description: str
