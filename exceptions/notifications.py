from fastapi import HTTPException, status
from constants.errors import NotificationErrors

class NotificationError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotificationNotInitializedError(NotificationError):
    def __init__(self):
        super().__init__(NotificationErrors.NOT_INITIALIZED, 500)
