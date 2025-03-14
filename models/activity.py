from dependencies.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ActivityType(Base):
    __tablename__ = "activity_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)

    activities = relationship("Activity", back_populates="type")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)

    # optional content for diferent types of activity
    topic = Column(String, nullable=True)
    speaker = Column(String, nullable=True)
    facilitator = Column(String, nullable=True)
    type_id = Column(Integer, ForeignKey("activity_types.id"), nullable=False)

    type = relationship("ActivityType", back_populates="activities")


