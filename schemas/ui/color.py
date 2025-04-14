from enum import Enum


class Color(str, Enum):
    """Enum for colors, including content colors"""
    PRIMARY = "primary"
    PRIMARY_CONTENT = "primary-content"
    SECONDARY = "secondary"
    SECONDARY_CONTENT = "secondary-content"
    SUCCESS = "success"
    SUCCESS_CONTENT = "success-content"
    DANGER = "danger"
    DANGER_CONTENT = "danger-content"
    WARNING = "warning"
    WARNING_CONTENT = "warning-content"
    INFO = "info"
    INFO_CONTENT = "info-content"
