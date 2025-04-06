from enum import Enum

class Color(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"

class BackgroundColor(str, Enum):
    """Enum for background colors"""
    PRIMARY = "bg-primary"
    SECONDARY = "bg-secondary"
    SUCCESS = "bg-success"
    DANGER = "bg-danger"
    WARNING = "bg-warning"
    INFO = "bg-info"

class TextColor(str, Enum):
    """Enum for text colors, including content colors"""
    PRIMARY = "text-primary"
    PRIMARY_CONTENT = "text-primary-content"
    SECONDARY = "text-secondary"
    SECONDARY_CONTENT = "text-secondary-content"
    SUCCESS = "text-success"
    SUCCESS_CONTENT = "text-success-content"
    DANGER = "text-danger"
    DANGER_CONTENT = "text-danger-content"
    WARNING = "text-warning"
    WARNING_CONTENT = "text-warning-content"
    INFO = "text-info"
    INFO_CONTENT = "text-info-content"

class BorderColor(str, Enum):
    """Enum for border colors"""
    PRIMARY = "border-primary"
    SECONDARY = "border-secondary"
    SUCCESS = "border-success"
    DANGER = "border-danger"
    WARNING = "border-warning"
    INFO = "border-info"

class ContentColor(str, Enum):
    """Enum for content colors (text on top of backgrounds)"""
    PRIMARY = "text-primary-content"
    SECONDARY = "text-secondary-content"
    SUCCESS = "text-success-content"
    DANGER = "text-danger-content"
    WARNING = "text-warning-content"
    INFO = "text-info-content"