from sqlalchemy.orm import Session
from models.message import Message, RecipientType
from schemas.notification import NotificationRequest
from services.groups import get_user_groups
from services.websocket_service import WebSocketService, WebSocketConnection
from typing import List, Dict, Set
import logging

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

    async def mark_notifications_read(self, user_id: str, notification_ids: List[str]):
        """Mark specified notifications as read"""
        if self.db is None:
            raise ValueError("NotificationService not initialized with a database session")

        self.db.query(Message).filter(
            Message.id.in_(notification_ids),
            Message.recipient == user_id
        ).update({Message.read: True})
        
        self.db.commit()

    async def handle_real_time_notification(self, notification: NotificationRequest):
        """
        Handle real-time notifications and send them directly to connected clients
        """
        try:
            # Handle different recipient types
            if notification.recipient_type == RecipientType.UNICAST:
                # Send to specific user's connections
                if notification.recipient in self.user_connections:
                    for connection in self.user_connections[notification.recipient]:
                        try:
                            await connection.send("notifications", notification)
                        except Exception as e:
                            logger.error(f"Error sending notification to user {notification.recipient}: {str(e)}")
                            self.remove_connection(connection)

            elif notification.recipient_type == RecipientType.MULTICAST:
                # Get users in the group and send to their connections
                group_id = notification.recipient
                for user_id, connections in self.user_connections.items():
                    user_groups = await get_user_groups(user_id)
                    if any(group["id"] == group_id for group in user_groups):
                        for connection in connections:
                            try:
                                await connection.send("notifications", notification)
                            except Exception as e:
                                logger.error(f"Error sending group notification to user {user_id}: {str(e)}")
                                self.remove_connection(connection)

            elif notification.recipient_type == RecipientType.BROADCAST:
                # Send to all connections (authenticated and anonymous)
                # First, send to all authenticated users
                for connections in self.user_connections.values():
                    for connection in connections:
                        try:
                            await connection.send("notifications", notification)
                        except Exception as e:
                            logger.error(f"Error sending broadcast to authenticated user: {str(e)}")
                            self.remove_connection(connection)

                # Then send to anonymous connections
                for connection in self.anonymous_connections:
                    try:
                        await connection.send("notifications", notification)
                    except Exception as e:
                        logger.error(f"Error sending broadcast to anonymous connection: {str(e)}")
                        self.remove_connection(connection)

            logger.info(f"Real-time notification sent: {notification}")
            logger.debug(f"Anonymous connections: {str(self.anonymous_connections)}")
        except Exception as e:
            logger.error(f"Error handling real-time notification: {str(e)}")

    async def get_user_notifications(self, user_id: str) -> List[Message]:
        """
        Get all undelivered notifications for a user, including individual notifications,
        notifications sent to their groups, and broadcast notifications.
        """
        if self.db is None:
            raise ValueError(
                "NotificationService not initialized with a database session")

        # Get user's groups
        user_groups = await get_user_groups(user_id)
        group_ids = [group["id"] for group in user_groups]

        # Query notifications
        notifications = self.db.query(Message).filter(
            Message.type == "in-app",
            Message.delivered == False,
            # Get notifications sent directly to the user, to any of their groups, or broadcasts
            (
                (Message.recipient_type == RecipientType.UNICAST) & (Message.recipient == user_id) |
                (Message.recipient_type == RecipientType.MULTICAST) & (Message.recipient.in_(group_ids)) |
                (Message.recipient_type == RecipientType.BROADCAST)
            )
        ).order_by(Message.created_at.desc()).all()

        # Mark notifications as delivered
        for notification in notifications:
            notification.delivered = True

        self.db.commit()

        return notifications

    async def get_broadcast_notifications(self) -> List[Message]:
        """
        Get all undelivered broadcast notifications.
        """
        if self.db is None:
            raise ValueError(
                "NotificationService not initialized with a database session")

        # Query broadcast notifications
        notifications = self.db.query(Message).filter(
            Message.type == "in-app",
            Message.delivered == False,
            Message.recipient_type == RecipientType.BROADCAST
        ).order_by(Message.created_at.desc()).all()

        return notifications
