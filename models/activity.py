from dependencies.database import Base
from sqlalchemy import  Column, \
                        Integer, \
                        String, \
                        Boolean, \
                        Time, \
                        ForeignKey
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy.orm import relationship

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    image = image_attachment("ActivityImage")
    date = Column(Time, nullable=True)
    duration = Column(Integer, nullable=True)

class ActivityImage(Base, Image):
    __tablename__ = "activity_images"

    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)
    activity = relationship("Activity")

class Talk(Activity):
    __tablename__ = "talks"

    speaker = Column(String, nullable=False)
    topic = Column(String, nullable=False)

class Workshop(Activity):
    __tablename__ = "workshops"

    facilitator = Column(String, nullable=False)
    topic = Column(String, nullable=False)