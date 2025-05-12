from exceptions.base import ServiceError
from constants.errors import ManifestErrors

class ManifestException(ServiceError):
    """Base exception for manifest related errors"""
    pass

class ManifestNotFoundError(ManifestException):
    """Raised when manifest is not found"""
    def __init__(self):
        super().__init__(ManifestErrors.NOT_FOUND, 404)

class ManifestUpdateError(ManifestException):
    """Raised when manifest update fails"""
    def __init__(self, error: str):
        super().__init__(ManifestErrors.UPDATE_ERROR.format(error=error), 400)

class ManifestInsertIconError(ManifestException):
    """Raised when icon insertion fails"""
    def __init__(self, error: str):
        super().__init__(ManifestErrors.INSERT_ICON_ERROR.format(error=error), 400)