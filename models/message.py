from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.types import Enum as SQLAlchemyEnum
from schemas.notification import RecipientType
from datetime import UTC, datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    recipient_type = Column(SQLAlchemyEnum(RecipientType), nullable=False)
    recipient = Column(String, nullable=True)  # Can be null for BROADCAST
    payload = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    delivered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
