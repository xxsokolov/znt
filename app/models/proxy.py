from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from app.databases.database import Base


class Proxy(Base):
    __tablename__ = "proxy"

    id = Column(Integer, primary_key=True, index=True)
    proto = Column(String, index=True, nullable=False)
    url = Column(String, index=True, nullable=False)
    description = Column(String, default=None, index=True)
    # bot = relationship("Bot", backref="proxy")
    bot = relationship("Bot", back_populates="proxy")

