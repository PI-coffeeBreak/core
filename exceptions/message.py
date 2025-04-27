from fastapi import HTTPException, status
from constants.errors import MessageErrors

class MessageError(HTTPException):
    """Base exception for message errors"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class MessageNotInitializedError(MessageError):
    """Raised when MessageBus is not initialized with a database session"""
    def __init__(self):
        super().__init__(
            detail=MessageErrors.NOT_INITIALIZED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MessageNotFoundError(MessageError):
    """Raised when message is not found"""
    def __init__(self, message_id: str):
        super().__init__(
            detail=MessageErrors.NOT_FOUND.format(message_id=message_id),
            status_code=status.HTTP_404_NOT_FOUND
        )

class MessageInvalidRecipientTypeError(MessageError):
    """Raised when recipient type is invalid"""
    def __init__(self, recipient_type: str):
        super().__init__(
            detail=MessageErrors.INVALID_RECIPIENT_TYPE.format(recipient_type=recipient_type),
            status_code=status.HTTP_400_BAD_REQUEST
        ) 