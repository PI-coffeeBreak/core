from typing import Dict, Type, Optional
from schemas.ui.page import BaseComponentSchema
from exceptions.component import ComponentInvalidBaseError, ComponentAlreadyRegisteredError, ComponentNotFoundError


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
            ComponentInvalidBaseError: If component doesn't inherit from BaseComponentSchema
            ComponentAlreadyRegisteredError: If component is already registered
        """
        if not issubclass(component_class, BaseComponentSchema):
            raise ComponentInvalidBaseError(component_class.__name__)

        component_name = component_class.__name__
        if component_name in cls._components:
            raise ComponentAlreadyRegisteredError(component_name)

        cls._components[component_name] = component_class

    @classmethod
    def get_component(cls, component_name: str) -> Optional[Type[BaseComponentSchema]]:
        """
        Get a registered component by name

        Args:
            component_name: Name of the component class

        Returns:
            Component class if found

        Raises:
            ComponentNotFoundError: If component is not found
        """
        component = cls._components.get(component_name)
        if not component:
            raise ComponentNotFoundError(component_name)
        return component

    @classmethod
    def list_components(cls) -> Dict[str, Type[BaseComponentSchema]]:
        """
        List all registered components

        Returns:
            Dictionary of component names and their classes
        """
        return cls._components.copy()

    @classmethod
    def unregister_component(cls, component_name: str) -> None:
        """
        Unregister a component by name

        Args:
            component_name: Name of the component class to unregister

        Raises:
            ComponentNotFoundError: If component is not found
        """
        if component_name not in cls._components:
            raise ComponentNotFoundError(component_name)
        del cls._components[component_name]
