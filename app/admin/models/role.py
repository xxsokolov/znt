# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import Column, Integer, String
from app.databases.database import Base


class Role(Base):

    __tablename__ = "role"

    id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
