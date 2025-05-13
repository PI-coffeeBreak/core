from .base import ServiceError
from constants.errors import ActivityTypeErrors

class ActivityTypeError(ServiceError):
    """Base exception for activity type errors"""
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail=detail, status_code=status_code)

class ActivityTypeNotFoundError(ActivityTypeError):
    """Raised when activity type is not found"""
    def __init__(self, type_id: int):
        super().__init__(
            detail=ActivityTypeErrors.NOT_FOUND.format(type_id=type_id),
            status_code=404
        )

class ActivityTypeValidationError(ActivityTypeError):
    """Raised when activity type validation fails"""
    def __init__(self, errors: list[str]):
        super().__init__(
            detail=ActivityTypeErrors.VALIDATION_FAILED.format(errors=errors),
            status_code=400
        )
