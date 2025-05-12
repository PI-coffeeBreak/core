from exceptions.base import ServiceError
from constants.errors import FaviconErrors

class FaviconException(ServiceError):
    """Base exception for favicon related errors"""
    pass

class FaviconNotFoundError(FaviconException):
    """Raised when favicon is not found"""
    def __init__(self):
        super().__init__(FaviconErrors.NOT_FOUND, 404)
