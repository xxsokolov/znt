# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from typing import Union
from pydantic import BaseModel


class BaseProxy(BaseModel):
    proto: str
    url: str
    description: Union[str, None] = None


class FullProxy(BaseProxy):
    id: int

    class Config:
        orm_mode = True
