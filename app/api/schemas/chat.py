# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from typing import List
from pydantic import BaseModel
from .topic import FullTopic


class BaseChat(BaseModel):
    name: str
    chat_id: int
    chat_id_prev: int = None
    description: str = None
    type: str


class FullChat(BaseChat):
    id: int
    topic: List[FullTopic] = []

    class Config:
        orm_mode = True
