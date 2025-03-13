from dependencies.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=True)
    date = Column(Time, nullable=True)
    duration = Column(Integer, nullable=True)
    type = Column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "activity",
        "polymorphic_on": type,
    }

class Talk(Activity):
    __tablename__ = "talks"
    id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

    speaker = Column(String, nullable=False)
    topic = Column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "talk",
    }

class Workshop(Activity):
    __tablename__ = "workshops"
    id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

    facilitator = Column(String, nullable=False)
    topic = Column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "workshop",
    }
