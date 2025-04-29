from fastapi import HTTPException, status
from constants.errors import EventErrors

class EventError(HTTPException):
    """Base exception for event errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class EventNotFoundError(EventError):
    """Raised when event is not found"""
    def __init__(self, event_id: str):
        super().__init__(
            detail=EventErrors.NOT_FOUND.format(event_id=event_id),
            status_code=status.HTTP_404_NOT_FOUND
        ) 