# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship
from flask_login import UserMixin

from app.databases.database import Base


class User(Base, UserMixin):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))

    # roles = relationship("Role", back_populates="user")
