from pydantic import BaseModel

class PluginAction(BaseModel):
    plugin_name: str

class PluginSettings(BaseModel):
    settings: dict
