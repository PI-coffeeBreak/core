from typing import List, Type, Any
from fastapi import HTTPException
from pydantic import BaseModel
from schemas.plugin_setting import PluginSetting
from dependencies.mongodb import db
from schemas.plugin_setting import ToggleInput, NumberInput, SelectorInput, TextInput, CheckboxInput
import logging

logger = logging.getLogger(__name__)

plugin_settings_collection = db['plugin_settings']

async def list_plugin_settings() -> List[PluginSetting]:
    plugin_settings = await plugin_settings_collection.find().to_list(None)
    return [PluginSetting(**plugin_setting) for plugin_setting in plugin_settings]

async def create_plugin_setting(plugin_setting: PluginSetting) -> PluginSetting:
    result = await plugin_settings_collection.insert_one(plugin_setting.model_dump())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create plugin setting")
    return plugin_setting

async def get_plugin_setting_by_title(plugin_title: str) -> PluginSetting:
    plugin_setting = await plugin_settings_collection.find_one({"title": plugin_title})
    if not plugin_setting:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    return PluginSetting(**plugin_setting)

async def update_plugin_setting_by_title(plugin_title: str, plugin_setting: PluginSetting) -> PluginSetting:
    result = await plugin_settings_collection.update_one(
        {"title": plugin_title},
        {"$set": plugin_setting.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update plugin setting")
    return plugin_setting

async def delete_plugin_setting_by_title(plugin_title: str) -> PluginSetting:
    plugin_setting = await plugin_settings_collection.find_one({"title": plugin_title})
    if not plugin_setting:
        raise HTTPException(status_code=404, detail="Plugin setting not found")
    result = await plugin_settings_collection.delete_one({"title": plugin_title})
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete plugin setting")
    return PluginSetting(**plugin_setting)

def generate_inputs_from_settings(settings_class: Type[BaseModel]) -> List[Any]:
    """
    Generate UI input components from a Pydantic settings class
    
    Args:
        settings_class: A Pydantic model class with Field annotations
        
    Returns:
        List of input components for the UI
    """
    inputs = []
    
    try:
        # Get the model schema
        schema = settings_class.model_json_schema()
        properties = schema.get('properties', {})
        
        # Process each field in the model
        for field_name, field_info in properties.items():
            try:
                # Get the field from the model
                field = settings_class.model_fields.get(field_name)
                if not field:
                    continue
                    
                # Get field metadata
                field_type = field.annotation
                field_default = field.default
                
                # Extract title and description
                title = field.json_schema_extra.get('title', field_name.replace('_', ' ').title()) if field.json_schema_extra else field_name.replace('_', ' ').title()
                description = field.json_schema_extra.get('description', "") if field.json_schema_extra else ""
                
                if field_type == bool:
                    # Boolean fields become toggles
                    inputs.append(ToggleInput(
                        title=title,
                        name=field_name,
                        description=description or "",
                        default=field_default
                    ))
                    
                elif field_type == int or field_type == float:
                    # Number fields
                    min_val = field.json_schema_extra.get('gt', 0) if field.json_schema_extra else 0
                    max_val = field.json_schema_extra.get('le', 100) if field.json_schema_extra else 100
                    step_val = 1
                    
                    inputs.append(NumberInput(
                        title=title,
                        name=field_name,
                        description=description or "",
                        min=min_val,
                        max=max_val,
                        step=step_val,
                        default=field_default or 0
                    ))
                    
                elif field_type == str:
                    # Check if we have options for a selector
                    options = field.json_schema_extra.get('options', None) if field.json_schema_extra else None
                    
                    if options:
                        # If options are provided, create a selector
                        inputs.append(SelectorInput(
                            title=title,
                            name=field_name,
                            description=description,
                            options=options,
                            default=field_default
                        ))
                    else:
                        # Otherwise create a text input
                        inputs.append(TextInput(
                            title=title,
                            name=field_name,
                            description=description,
                            default=field_default
                        ))
                        
                elif field_type == List[str] or str(field_type).startswith('list'):
                    # List fields become checkboxes
                    options = field.json_schema_extra.get('options', []) if field.json_schema_extra else []
                    
                    inputs.append(CheckboxInput(
                        title=title,
                        name=field_name,
                        description=description,
                        options=options,
                        default=field_default
                    ))
                    
                else:
                    # Default to text input for other types
                    inputs.append(TextInput(
                        title=title,
                        name=field_name,
                        description=description or "",
                        default=""
                    ))
            except Exception as e:
                logger.error(f"Error processing field {field_name}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error generating inputs: {e}")
        return []
        
    return inputs
