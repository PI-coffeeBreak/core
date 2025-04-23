from dependencies.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.types import Enum as SQLAlchemyEnum
from schemas.notification import RecipientType
from datetime import UTC, datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_type = Column(SQLAlchemyEnum(RecipientType), nullable=False)
    recipient = Column(String, nullable=True)  # Can be null for BROADCAST
    payload = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

class NotificationRead(Base):
    __tablename__ = "notification_reads"

    notification_id = Column(Integer, ForeignKey("notifications.id"), primary_key=True)
    user_id = Column(String, primary_key=True)
    read_at = Column(DateTime, default=datetime.now(UTC)) 