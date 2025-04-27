from fastapi import HTTPException, status
from constants.errors import ComponentErrors

class ComponentError(HTTPException):
    """Base exception for component errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ComponentInvalidBaseError(ComponentError):
    """Raised when component doesn't inherit from BaseComponentSchema"""
    def __init__(self, component_name: str):
        super().__init__(
            detail=ComponentErrors.INVALID_BASE.format(component_name=component_name),
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ComponentAlreadyRegisteredError(ComponentError):
    """Raised when component is already registered"""
    def __init__(self, component_name: str):
        super().__init__(
            detail=ComponentErrors.ALREADY_REGISTERED.format(component_name=component_name),
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ComponentNotFoundError(ComponentError):
    """Raised when component is not found"""
    def __init__(self, component_name: str):
        super().__init__(
            detail=ComponentErrors.NOT_FOUND.format(component_name=component_name),
            status_code=status.HTTP_404_NOT_FOUND
        ) 