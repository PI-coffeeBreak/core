from enum import Enum


class Color(str, Enum):
    """Enum for DaisyUI theme colors"""
    # Base colors
    BASE_100 = "base-100"
    BASE_200 = "base-200"
    BASE_300 = "base-300"
    BASE_CONTENT = "base-content"

    # Main theme colors
    PRIMARY = "primary"
    PRIMARY_CONTENT = "primary-content"
    SECONDARY = "secondary"
    SECONDARY_CONTENT = "secondary-content"
    ACCENT = "accent"
    ACCENT_CONTENT = "accent-content"
    NEUTRAL = "neutral"
    NEUTRAL_CONTENT = "neutral-content"

    # State colors
    INFO = "info"
    INFO_CONTENT = "info-content"
    SUCCESS = "success"
    SUCCESS_CONTENT = "success-content"
    WARNING = "warning"
    WARNING_CONTENT = "warning-content"
    ERROR = "error"
    ERROR_CONTENT = "error-content"
