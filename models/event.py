from sqlalchemy import Column, Integer, String, DateTime, JSON
from dependencies.database import Base
from datetime import datetime, UTC

class Event(Base):
    __tablename__ = "events"    

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    payload = Column(String)
    details = Column(JSON)