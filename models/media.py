from sqlalchemy import Column, String, Integer, Boolean, JSON
from dependencies.database import Base


class Media(Base):
    """
    Entity for managing media files metadata
    """
    __tablename__ = 'media'

    uuid = Column(String, primary_key=True)
    max_size = Column(Integer, nullable=True)
    hash = Column(String, nullable=True)
    alias = Column(String, nullable=True)
    valid_extensions = Column(JSON, default=list)
    allow_rewrite = Column(Boolean, default=True)
    op_required = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Media(uuid='{self.uuid}', alias='{self.alias}', hash='{self.hash}')>"
