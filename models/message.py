from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.types import Enum as SQLAlchemyEnum
from enum import Enum as PyEnum

class RecipientType(PyEnum):
    SINGLE = "SINGLE"
    GROUP = "GROUP"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    recipient_type = Column(SQLAlchemyEnum(RecipientType), nullable=False)
    recipient = Column(Integer, nullable=False)
    payload = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    delivered = Column(Boolean, default=False)