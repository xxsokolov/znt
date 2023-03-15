# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.databases.database import Base


class Bot(Base):

    __tablename__ = "bot"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    group = Column(String, default=None, index=True)
    token = Column(String, index=True, nullable=False)
    description = Column(String, default=None, index=True)
    priority = Column(Integer, default=0, index=True, nullable=False)
    proxy_use = Column(Boolean, default=False, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    proxy_id = Column(Integer, ForeignKey("proxy.id"))
    proxy = relationship("Proxy", back_populates="bot")
    # proxy = relationship("Proxy", primaryjoin="Proxy.id == Bot.proxy_id", cascade="all, delete-orphan")

