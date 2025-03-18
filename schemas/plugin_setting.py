from typing import List, Union
from pydantic import BaseModel

class SelectorInput(BaseModel):
    type: str
    title: str
    description: str
    options: List[str]

class TextInput(BaseModel):
    type: str
    title: str

class ShortTextInput(BaseModel):
    type: str
    title: str

class CheckboxInput(BaseModel):
    type: str
    kind: List[str]
    title: str
    options: List[str]

class ComposedTextInput(BaseModel):
    type: str
    title: str
    name: str
    description: str

class PluginSetting(BaseModel):
    title: str
    description: str
    inputs: List[Union[SelectorInput, TextInput, ShortTextInput, CheckboxInput, ComposedTextInput]]



# Example usage
example_json = {
    "title": "Plugin Name",
    "description": "Plugin Description",
    "inputs": [
        {
            "type": "selector",
            "title": "title",
            "description": "description",
            "options": ["op1", "op2", "op3"]
        },
        {
            "type": "text",
            "title": "title"
        },
        {
            "type": "shortText",
            "title": "title"
        },
        {
            "type": "checkbox",
            "kind": ["multiple", "single", "toggle"],
            "title": "title",
            "options": ["op1", "op2", "op3"]
        },
        {
            "type": "composedText",
            "title": "title",
            "name": "name",
            "description": "description"
        }
    ]
}

plugin_setting = PluginSetting(**example_json)
print(plugin_setting)