from exceptions.base import \
    ServiceError

from exceptions.activity import \
    ActivityError, \
    ActivityNotFoundError, \
    ActivityNoImageError, \
    ActivityValidationError, \
    ActivityImageNotFoundError, \
    ActivityRequiresManageError

from exceptions.activity_type import \
    ActivityTypeError, \
    ActivityTypeNotFoundError, \
    ActivityTypeValidationError

from exceptions.media import \
    MediaError, \
    MediaNotFoundError, \
    MediaNoExtensionError, \
    MediaRequiresOpError, \
    MediaNoRewriteError, \
    MediaNoDeleteError, \
    MediaHasFileError

from exceptions.event import \
    EventError, \
    EventNotFoundError

from exceptions.message import \
    MessageError, \
    MessageNotInitializedError, \
    MessageNotFoundError, \
    MessageInvalidRecipientTypeError

from exceptions.component import \
    ComponentError, \
    ComponentInvalidBaseError, \
    ComponentAlreadyRegisteredError, \
    ComponentNotFoundError

from exceptions.notifications import \
    NotificationError, \
    NotificationNotInitializedError

from exceptions.plugin import \
    PluginError, \
    PluginNotFoundError, \
    PluginNotLoadedError, \
    PluginSettingsError

from exceptions.manifest import \
    ManifestException, \
    ManifestNotFoundError, \
    ManifestUpdateError, \
    ManifestInsertIconError

from exceptions.favicon import \
    FaviconException, \
    FaviconNotFoundError

from exceptions.user import \
    UserError, \
    UserNotFoundError, \
    UserListError, \
    UserCreateError, \
    UserUpdateError, \
    UserDeleteError, \
    UserRoleError

from exceptions.group import \
    GroupError, \
    GroupNotFoundError, \
    GroupListError, \
    GroupCreateError, \
    GroupAddUserError, \
    GroupGetUsersError

__all__ = [
    "ServiceError",
    "ActivityError",
    "ActivityNotFoundError",
    "ActivityNoImageError",
    "ActivityValidationError",
    "ActivityImageNotFoundError",
    "ActivityRequiresManageError",
    "ActivityTypeError",
    "ActivityTypeNotFoundError",
    "ActivityTypeValidationError",
    "MediaError",
    "MediaNotFoundError",
    "MediaNoExtensionError",
    "MediaRequiresOpError",
    "MediaNoRewriteError",
    "MediaNoDeleteError",
    "MediaHasFileError",
    "EventError",
    "EventNotFoundError",
    "MessageError",
    "MessageNotInitializedError",
    "MessageNotFoundError",
    "MessageInvalidRecipientTypeError",
    "ComponentError",
    "ComponentInvalidBaseError",
    "ComponentAlreadyRegisteredError",
    "ComponentNotFoundError",
    "NotificationError",
    "NotificationNotInitializedError",
    "PluginError",
    "PluginNotFoundError",
    "PluginNotLoadedError",
    "PluginSettingsError",
    "UserError",
    "UserNotFoundError",
    "UserListError",
    "UserCreateError",
    "UserUpdateError",
    "UserDeleteError",
    "UserRoleError",
    "GroupError",
    "GroupNotFoundError",
    "GroupListError",
    "GroupCreateError",
    "GroupAddUserError",
    "GroupGetUsersError",
    "ManifestException",
    "ManifestNotFoundError",
    "ManifestUpdateError",
    "ManifestInsertIconError",
    "FaviconException",
    "FaviconNotFoundError"
]