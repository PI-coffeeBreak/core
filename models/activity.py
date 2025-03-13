from dependencies.database import Base
from sqlalchemy import  Column, \
                        Integer, \
                        String, \
                        Boolean

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    date = Column(String, nullable=False)
    duration = Column(String, nullable=False)

class Talk(Activity):
    __tablename__ = "talks"

    speaker = Column(String, nullable=False)
    topic = Column(String, nullable=False)

class Workshop(Activity):
    __tablename__ = "workshops"

    facilitator = Column(String, nullable=False)
    topic = Column(String, nullable=False)