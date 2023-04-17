# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from pydantic import BaseModel


class BaseTopic(BaseModel):
    name: str
    topic_id: int
    chat_id: str


class FullTopic(BaseTopic):
    id: int
    # chat: FullChat = None

    class Config:
        orm_mode = True
