# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from pydantic import BaseModel


class BaseChat(BaseModel):
    name: str
    chat_id: int
    chat_id_prev: int = None
    description: str = None
    type: str


class FullChat(BaseChat):
    id: int

    class Config:
        orm_mode = True
