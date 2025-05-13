from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from dependencies.database import Base

class Event(Base):
    __tablename__ = "event_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    
    # Change from direct image storage to media reference
    image_id = Column(String, ForeignKey("media.uuid"), nullable=True)
    image = relationship("Media")