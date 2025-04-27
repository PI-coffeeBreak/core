from typing import List
from constants.errors import ActivityErrors
from .base import ServiceError


class ActivityError(ServiceError):
    """Base exception for activity service errors"""
    pass

class ActivityNotFoundError(ActivityError):
    """Raised when an activity is not found"""
    def __init__(self, activity_id: int):
        super().__init__(ActivityErrors.NOT_FOUND.format(activity_id=activity_id), 404)


class ActivityNoImageError(ActivityError):
    """Raised when trying to remove an image from an activity that has no image"""
    def __init__(self, activity_id: int):
        super().__init__(ActivityErrors.NO_IMAGE.format(activity_id=activity_id), 400)


class ActivityValidationError(ActivityError):
    """Raised when activity data validation fails"""
    def __init__(self, errors: List[str]):
        super().__init__(
            ActivityErrors.VALIDATION_FAILED.format(errors="; ".join(errors)),
            400
        )


class ActivityImageNotFoundError(ActivityError):
    """Raised when activity image is not found"""
    def __init__(self):
        super().__init__(ActivityErrors.IMAGE_NOT_FOUND, 404)


class ActivityRequiresManageError(ActivityError):
    """Raised when operation requires manage_activities role"""
    def __init__(self):
        super().__init__(ActivityErrors.REQUIRES_MANAGE, 403) 