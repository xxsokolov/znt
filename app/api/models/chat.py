# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import Numeric, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.databases.database import Base


class Chat(Base):

    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    chat_id = Column(Numeric, index=True, nullable=False)
    chat_id_prev = Column(Numeric, index=True)
    type = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    # topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship("Topic", back_populates="chat")
