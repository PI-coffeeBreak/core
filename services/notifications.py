from sqlalchemy.orm import Session
from models.message import Message, RecipientType
from services.groups import get_user_groups
from typing import List


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
            self._initialized = True
        elif db is not None:
            self.db = db

    async def get_user_notifications(self, user_id: str) -> List[Message]:
        """
        Get all undelivered notifications for a user, including both individual notifications
        and notifications sent to their groups.
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
            # Get notifications sent directly to the user or to any of their groups
            (
                (Message.recipient_type == RecipientType.UNICAST) & (Message.recipient == user_id) |
                (Message.recipient_type == RecipientType.MULTICAST) & (
                    Message.recipient.in_(group_ids))
            )
        ).all()

        # Mark notifications as delivered
        for notification in notifications:
            notification.delivered = True

        self.db.commit()

        return notifications
