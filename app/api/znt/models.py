from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from . import schemas
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Bot(Base):

    __tablename__ = "bot"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, Enum(schemas.TypeBot, name="type_bot_enum", create_type=False), index=True, nullable=False)
    token = Column(String, index=True, nullable=False)
    description = Column(String, default=None, index=True)
    priority = Column(Integer, default=0, index=True, nullable=False)

    proxys = relationship("Proxy", back_populates="bot")


class Proxy(Base):
    __tablename__ = "proxy"

    id = Column(Integer, primary_key=True, index=True)
    proto = Column(String, index=True, nullable=False)
    url = Column(String, index=True, nullable=False)
    description = Column(String, default=None, index=True)

    bot_id = Column(Integer, ForeignKey("bot.id"))

    bot = relationship("Bot", back_populates="proxys")

