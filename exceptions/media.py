from typing import List
from constants.errors import MediaErrors
from .base import ServiceError


class MediaError(ServiceError):
    """Base exception for media service errors"""
    pass


class MediaNotFoundError(MediaError):
    """Raised when media is not found"""
    def __init__(self):
        super().__init__(MediaErrors.NOT_FOUND, 404)


class MediaAlreadyExistsError(MediaError):
    """Raised when trying to create media that already exists"""
    def __init__(self):
        super().__init__(MediaErrors.ALREADY_EXISTS, 400)


class MediaFileTooLargeError(MediaError):
    """Raised when file size exceeds limit"""
    def __init__(self, max_size: int):
        super().__init__(MediaErrors.FILE_TOO_LARGE.format(max_size), 400)


class MediaInvalidExtensionError(MediaError):
    """Raised when file extension is not allowed"""
    def __init__(self, valid_extensions: List[str]):
        super().__init__(MediaErrors.INVALID_EXTENSION.format(', '.join(valid_extensions)), 400)


class MediaNoExtensionError(MediaError):
    """Raised when file has no extension"""
    def __init__(self):
        super().__init__(MediaErrors.NO_EXTENSION, 400)


class MediaRequiresOpError(MediaError):
    """Raised when operation requires media_op role"""
    def __init__(self):
        super().__init__(MediaErrors.REQUIRES_OP, 403)


class MediaNoRewriteError(MediaError):
    """Raised when rewrite is not allowed"""
    def __init__(self):
        super().__init__(MediaErrors.NO_REWRITE, 403)


class MediaNoDeleteError(MediaError):
    """Raised when delete is not allowed"""
    def __init__(self):
        super().__init__(MediaErrors.NO_DELETE, 403)


class MediaHasFileError(MediaError):
    """Raised when trying to unregister media with file"""
    def __init__(self):
        super().__init__(MediaErrors.HAS_FILE, 400) 