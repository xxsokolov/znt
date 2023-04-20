# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import Query
from pydantic import BaseModel
from .proxy import FullProxy

# class TypeBot(str, Enum):
#     prod = "production"
#     dev = "develop"
#     test = "test"


class BaseBot(BaseModel):
    name: str = Query(default=None, regex="^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)")
    group: str = None
    description: str = None
    priority: int = 0


class AddBot(BaseBot):
    token: str = None


class DeleteBot(BaseBot):
    pass


class FullBot(BaseBot):
    id: int
    proxy_use: bool = False
    proxy: FullProxy = None

    class Config:
        orm_mode = True
