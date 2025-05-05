from typing import List, Union, Optional
from pydantic import BaseModel

class SelectorInput(BaseModel):
    type: str = "selector"
    title: str
    description: str
    options: List[str]

class TextInput(BaseModel):
    type: str = "text"
    title: str
    description: Optional[str] = None
    placeholder: Optional[str] = None

class ShortTextInput(BaseModel):
    type: str = "shortText"
    title: str
    description: Optional[str] = None
    placeholder: Optional[str] = None
    max_length: Optional[int] = 250

class ToggleInput(BaseModel):
    type: str = "toggle"
    title: str
    description: Optional[str] = None
    text: Optional[str] = None
    default: bool = False
    required: bool = False

class CheckboxInput(BaseModel):
    type: str = "checkbox"
    title: str
    description: Optional[str] = None
    options: List[str]  # Options to select from
    default: Optional[List[str]] = None  # Default selected options

class RadioInput(BaseModel):
    type: str = "radio"
    title: str
    description: Optional[str] = None
    options: List[str]  # Options to select from
    default: Optional[str] = None
    required: bool = False

class ComposedTextInput(BaseModel):
    type: str = "composedText"
    title: str
    name: str
    description: str

class NumberInput(BaseModel):
    type: str = "number"
    title: str
    description: str
    min: int
    max: int
    step: int
    default: int

class PluginSetting(BaseModel):
    title: str
    description: str
    inputs: List[Union[SelectorInput, TextInput, ShortTextInput, CheckboxInput, ToggleInput, RadioInput, ComposedTextInput, NumberInput]]

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