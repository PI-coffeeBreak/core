from sqlalchemy.orm import Session
from models.notification import Notification, NotificationRead
from models.message import RecipientType
from schemas.notification import NotificationRequest, NotificationResponse
from services.groups import get_user_groups
from services.websocket_service import WebSocketService, WebSocketConnection
from services.message_bus import MessageBus
from typing import List, Dict, Set
import logging
import asyncio
from exceptions.notifications import (
    NotificationNotInitializedError
)

logger = logging.getLogger("coffeebreak.notifications")


class NotificationService:
    _instance = None
    _initialized = False

    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
        return cls._instance

    def __init__(self, db: Session = None):
        if not self._initialized:
            self.db = db
            # Store connections by user_id for authenticated users
            self.user_connections: Dict[str, Set[WebSocketConnection]] = {}
            # Store anonymous connections for broadcast messages
            self.anonymous_connections: Set[WebSocketConnection] = set()
            # Register handler for in-app notifications
            message_bus = MessageBus(db)
            asyncio.create_task(message_bus.register_message_handler("in-app", self.handle_in_app_message))
            self._initialized = True
        elif db is not None:
            self.db = db

    def add_connection(self, connection: WebSocketConnection) -> None:
        """Add a WebSocket connection to the appropriate collection"""
        if connection.is_authenticated():
            if connection.user_id not in self.user_connections:
                self.user_connections[connection.user_id] = set()
            self.user_connections[connection.user_id].add(connection)
            logger.debug(f"Added authenticated connection for user {connection.user_id}")
        else:
            self.anonymous_connections.add(connection)
            logger.debug("Added anonymous connection")

    def remove_connection(self, connection: WebSocketConnection) -> None:
        """Remove a WebSocket connection from the appropriate collection"""
        if connection.is_authenticated():
            if connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
                logger.debug(f"Removed authenticated connection for user {connection.user_id}")
        else:
            self.anonymous_connections.discard(connection)
            logger.debug("Removed anonymous connection")

    async def mark_notifications_read(self, user_id: str, notification_ids: List[int]):
        """Mark specified notifications as read"""
        if self.db is None:
            raise NotificationNotInitializedError()

        for notification_id in notification_ids:
            notification_read = NotificationRead(
                notification_id=notification_id,
                user_id=user_id
            )
            self.db.add(notification_read)
        
        self.db.commit()

    async def _send_to_connection(self, connection: WebSocketConnection, notification_response: dict, user_id: str = None):
        """Send notification to a single connection"""
        try:
            await connection.send("notifications", {
                "action": "new_notification",
                "notification": notification_response
            })
        except Exception as e:
            error_context = f"user {user_id}" if user_id else "anonymous connection"
            logger.error(f"Error sending notification to {error_context}: {str(e)}")
            self.remove_connection(connection)

    async def _send_to_user_connections(self, user_id: str, notification_response: dict):
        """Send notification to all connections of a specific user"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await self._send_to_connection(connection, notification_response, user_id)

    async def _send_to_group_members(self, group_id: str, notification_response: dict):
        """Send notification to all members of a group"""
        for user_id, connections in self.user_connections.items():
            user_groups = await get_user_groups(user_id)
            if any(group["id"] == group_id for group in user_groups):
                await self._send_to_user_connections(user_id, notification_response)

    async def _send_broadcast(self, notification_response: dict):
        """Send notification to all connected users and anonymous connections"""
        for connections in self.user_connections.values():
            for connection in connections:
                await self._send_to_connection(connection, notification_response)

        for connection in self.anonymous_connections:
            await self._send_to_connection(connection, notification_response)

    async def handle_in_app_message(self, notification: NotificationRequest):
        """Handler for in-app messages registered with the message bus"""
        if self.db is None:
            logger.error("NotificationService not properly initialized")
            return

        new_notification = Notification(
            recipient_type=notification.recipient_type,
            recipient=notification.recipient,
            payload=notification.payload
        )
        
        self.db.add(new_notification)
        self.db.commit()
        self.db.refresh(new_notification)  # Refresh to get the id and created_at
        
        # Use the created notification for real-time updates
        await self.handle_real_time_notification(new_notification)

    async def handle_real_time_notification(self, notification: Notification):
        """Handle real-time notifications and send them directly to connected clients"""
        try:
            # Convert notification to response format
            notification_response = NotificationResponse.model_validate(notification).model_dump()
            
            if notification.recipient_type == RecipientType.UNICAST:
                await self._send_to_user_connections(notification.recipient, notification_response)

            elif notification.recipient_type == RecipientType.MULTICAST:
                await self._send_to_group_members(notification.recipient, notification_response)

            elif notification.recipient_type == RecipientType.BROADCAST:
                await self._send_broadcast(notification_response)

            logger.info(f"Real-time notification sent: {notification}")
            logger.debug(f"Anonymous connections: {str(self.anonymous_connections)}")
        except Exception as e:
            logger.error(f"Error handling real-time notification: {str(e)}")

    async def get_user_notifications(self, user_id: str) -> List[Notification]:
        """
        Get all unread notifications for a user, including individual notifications,
        notifications sent to their groups, and broadcast notifications.
        """
        if self.db is None:
            raise NotificationNotInitializedError()

        # Get user's groups
        user_groups = await get_user_groups(user_id)
        group_ids = [group["id"] for group in user_groups]

        # Query notifications that haven't been read by the user
        notifications = self.db.query(Notification).filter(
            ~Notification.id.in_(
                self.db.query(NotificationRead.notification_id).filter(
                    NotificationRead.user_id == user_id
                )
            ),
            # Get notifications sent directly to the user, to any of their groups, or broadcasts
            (
                (Notification.recipient_type == RecipientType.UNICAST) & (Notification.recipient == user_id) |
                (Notification.recipient_type == RecipientType.MULTICAST) & (Notification.recipient.in_(group_ids)) |
                (Notification.recipient_type == RecipientType.BROADCAST)
            )
        ).order_by(Notification.created_at.desc()).all()

        return notifications

    async def get_broadcast_notifications(self) -> List[Notification]:
        """
        Get all broadcast notifications.
        """
        if self.db is None:
            raise NotificationNotInitializedError()

        # Query broadcast notifications
        notifications = self.db.query(Notification).filter(
            Notification.recipient_type == RecipientType.BROADCAST
        ).order_by(Notification.created_at.desc()).all()

        return notifications
