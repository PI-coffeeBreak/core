from typing import Dict
from pydantic import BaseModel


class ComponentInfo(BaseModel):
    """
    Schema for component information response

    Attributes:
        name (str): Name of the component
        schema (Dict): JSON Schema of the component
    """
    name: str
    schema: Dict


class ComponentsList(BaseModel):
    """
    Schema for listing all components

    Attributes:
        components (Dict[str, Dict]): Dictionary mapping component names to their schemas
    """
    components: Dict[str, Dict]
