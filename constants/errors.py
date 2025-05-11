from enum import StrEnum

class MediaErrors(StrEnum):
    """Media service error messages"""
    NOT_FOUND = "Media not found"
    ALREADY_EXISTS = "Media already exists"
    NO_EXTENSION = "File has no extension"
    INVALID_EXTENSION = "Invalid file extension. Allowed extensions: {}"
    FILE_TOO_LARGE = "File exceeds maximum size of {} bytes"
    NO_REWRITE = "Media does not allow rewrite"
    NO_DELETE = "Media does not allow deletion"
    REQUIRES_OP = "Operation requires media_op role"
    HAS_FILE = "Cannot unregister media with existing file"

class ActivityErrors(StrEnum):
    """Activity service error messages"""
    NOT_FOUND = "Activity with id {activity_id} not found"
    NO_IMAGE = "Activity with id {activity_id} has no image"
    VALIDATION_FAILED = "Activity validation failed: {errors}"
    IMAGE_NOT_FOUND = "Activity image not found"
    REQUIRES_MANAGE = "Operation requires manage_activities role"
    NAME_REQUIRED = "Name is required"
    NAME_TOO_LONG = "Name must be less than {max_length} characters"
    DESCRIPTION_TOO_LONG = "Description must be less than {max_length} characters"
    START_TIME_AFTER_END = "Activity duration must be greater than 0"

class ActivityTypeErrors(StrEnum):
    """Activity type service error messages"""
    NOT_FOUND = "Activity type with id {type_id} not found"
    NAME_REQUIRED = "Type is required"
    NAME_TOO_LONG = "Type must be less than {max_length} characters"
    DESCRIPTION_TOO_LONG = "Description must be less than {max_length} characters"
    REQUIRES_MANAGE = "Operation requires manage_activities role"

class EventErrors(StrEnum):
    """Event service error messages"""
    NOT_FOUND = "Event with id {event_id} not found"

class MessageErrors(StrEnum):
    """Message service error messages"""
    NOT_INITIALIZED = "MessageBus not initialized with a database session"
    NOT_FOUND = "Message with id {message_id} not found"
    INVALID_RECIPIENT_TYPE = "Invalid recipient type: {recipient_type}"

class ComponentErrors(StrEnum):
    """Component service error messages"""
    INVALID_BASE = "Component class {component_name} must inherit from BaseComponentSchema"
    ALREADY_REGISTERED = "Component {component_name} is already registered"
    NOT_FOUND = "Component {component_name} not found"

class NotificationErrors(StrEnum):
    """Notification service error messages"""
    NOT_INITIALIZED = "NotificationService not initialized with a database session"

class PluginErrors(StrEnum):
    """Plugin service error messages"""
    NOT_FOUND = "Plugin {plugin_name} not found"
    NOT_LOADED = "Plugin {plugin_name} is not loaded"
    SETTINGS_ERROR = "Error updating settings for plugin {plugin_name}"

class UserErrors(StrEnum):
    """User service error messages"""
    NOT_FOUND = "User with id {user_id} not found"
    LIST_ERROR = "Failed to list users: {error}"
    CREATE_ERROR = "Failed to create user: {error}"
    UPDATE_ERROR = "Failed to update user: {error}"
    DELETE_ERROR = "Failed to delete user: {error}"
    ROLE_ERROR = "Failed to assign role: {error}"

class GroupErrors(StrEnum):
    """Group service error messages"""
    NOT_FOUND = "Group '{group_name}' not found"
    LIST_ERROR = "Failed to list groups: {error}"
    CREATE_ERROR = "Failed to create group: {error}"
    ADD_USER_ERROR = "Failed to add user to group: {error}"
    GET_USERS_ERROR = "Failed to get users in group: {error}"

class ManifestErrors(StrEnum):
    """Manifest service error messages"""
    NOT_FOUND = "Manifest not found"
    UPDATE_ERROR = "Failed to update manifest: {error}"
    INSERT_ICON_ERROR = "Failed to insert icon: {error}"
