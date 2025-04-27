from fastapi import HTTPException, status
from constants.errors import ActivityTypeErrors

class ActivityTypeError(HTTPException):
    """Base exception for activity type errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ActivityTypeNotFoundError(ActivityTypeError):
    """Raised when activity type is not found"""
    def __init__(self, type_id: int):
        super().__init__(
            detail=ActivityTypeErrors.NOT_FOUND.format(type_id=type_id),
            status_code=status.HTTP_404_NOT_FOUND
        )

class ActivityTypeValidationError(ActivityTypeError):
    """Raised when activity type validation fails"""
    def __init__(self, errors: list[str]):
        super().__init__(
            detail=ActivityTypeErrors.VALIDATION_FAILED.format(errors=errors),
            status_code=status.HTTP_400_BAD_REQUEST
        )
