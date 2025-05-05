from typing import List, Union, Optional
from pydantic import BaseModel

class SelectorInput(BaseModel):
    type: str = "selector"
    title: str
    name: Optional[str] = None
    description: str
    options: List[str]

class TextInput(BaseModel):
    type: str = "text"
    title: str
    name: Optional[str] = None
    description: Optional[str] = None
    placeholder: Optional[str] = None
    max_length: Optional[int] = None
    default: Optional[str] = None

class ToggleInput(BaseModel):
    type: str = "toggle"
    title: str
    name: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    default: bool = False
    required: bool = False

class CheckboxInput(BaseModel):
    type: str = "checkbox"
    title: str
    name: Optional[str] = None
    description: Optional[str] = None
    options: List[str]
    default: Optional[List[str]] = None

class NumberInput(BaseModel):
    type: str = "number"
    title: str
    name: Optional[str] = None
    description: str = ""
    min: int = 0
    max: int = 100
    step: int = 1
    default: int = 0

class PluginSetting(BaseModel):
    title: str
    name: Optional[str] = None
    description: str
    inputs: List[Union[SelectorInput, TextInput, CheckboxInput, ToggleInput, NumberInput]]

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
            "title": "title",
            "description": "description",
            "options": ["op1", "op2", "op3"],
            "multiple": True,
            "default": ["op1"],
            "required": False
        },
        {
            "type": "toggle",
            "title": "title",
            "description": "description",
            "default": True,
            "required": False
        },
        {
            "type": "radio",
            "title": "title",
            "description": "description",
            "options": ["op1", "op2", "op3"],
            "default": "op1",
            "required": False
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