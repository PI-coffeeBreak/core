from .message_bus import MessageBus
from .notifications import NotificationService
import logging

logger = logging.getLogger(__name__)


async def register_notification_handlers(message_bus: MessageBus, notification_service: NotificationService):
    """
    Register all notification handlers with the message bus
    """
    # Register handler for in-app notifications
    await message_bus.register_message_handler(
        "in-app",
        notification_service.handle_real_time_notification
    )

    logger.info("Registered notification handlers")
