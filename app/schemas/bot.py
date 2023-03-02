from typing import Union, Optional, List
from fastapi import Query

from pydantic import BaseModel, Field
from enum import Enum
from app.schemas.proxy import *


class TypeBot(str, Enum):
    prod = "production"
    dev = "develop"
    test = "test"


class BaseBot(BaseModel):
    name: str = Query(default=None, regex="^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)")
    description: str
    type: TypeBot
    priority: int = 0


class AddBot(BaseBot):
    token: str = None


class FullBot(BaseBot):
    id: int
    proxy_use: bool = False
    proxy: FullProxy = None

    class Config:
        orm_mode = True





