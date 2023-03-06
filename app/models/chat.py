from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.databases.database import Base


class Chat(Base):

    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    chat_id = Column(Integer, index=True, nullable=False)
    chat_id_prev = Column(Integer, index=True)
    type = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
