from typing import Dict, Type, Optional
from schemas.ui.page import BaseComponentSchema


class ComponentRegistry:
    """
    Service responsible for registering and managing UI components
    Stores components in memory for easy access
    """
    _instance = None
    _components: Dict[str, Type[BaseComponentSchema]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register_component(cls, component_class: Type[BaseComponentSchema]) -> None:
        """
        Register a new component class

        Args:
            component_class: Component class that inherits from BaseComponentSchema

        Raises:
            ValueError: If component is already registered or doesn't inherit from BaseComponentSchema
        """
        if not issubclass(component_class, BaseComponentSchema):
            raise ValueError(
                f"Component class {component_class.__name__} must inherit from BaseComponentSchema")

        component_name = component_class.__name__
        if component_name in cls._components:
            raise ValueError(
                f"Component {component_name} is already registered")

        cls._components[component_name] = component_class

    @classmethod
    def get_component(cls, component_name: str) -> Optional[Type[BaseComponentSchema]]:
        """
        Get a registered component by name

        Args:
            component_name: Name of the component class

        Returns:
            Component class if found, None otherwise
        """
        return cls._components.get(component_name)

    @classmethod
    def list_components(cls) -> Dict[str, Type[BaseComponentSchema]]:
        """
        List all registered components

        Returns:
            Dictionary of component names and their classes
        """
        return cls._components.copy()

    @classmethod
    def unregister_component(cls, component_name: str) -> bool:
        """
        Unregister a component by name

        Args:
            component_name: Name of the component class to unregister

        Returns:
            True if component was unregistered, False if not found
        """
        if component_name in cls._components:
            del cls._components[component_name]
            return True
        return False
