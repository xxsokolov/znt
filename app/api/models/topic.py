# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import Numeric, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.databases.database import Base


class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    topic_id = Column(Numeric, index=True, nullable=False)
    # chat_id = relationship("Chat", back_populates="topic")
    chat_id = Column(Integer, ForeignKey("chat.id"))
    chat = relationship("Chat", back_populates="topic")
