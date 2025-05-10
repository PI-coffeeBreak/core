from sqlalchemy import Column, Integer, String, ForeignKey
from dependencies.database import Base
from sqlalchemy.orm import relationship

class ActivityOwner(Base):
    __tablename__ = "activity_owners"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(String, nullable=False)

    activity = relationship("Activity", back_populates="owners")
