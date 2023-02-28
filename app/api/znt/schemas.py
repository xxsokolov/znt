from typing import Union, Optional

from pydantic import BaseModel
from enum import Enum

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True








class ProxyBase(BaseModel):
    url: str
    description: Union[str, None] = None


class ProxyAdd(ProxyBase):
    pass


class Proxy(ProxyBase):
    id: int
    bot_id: int

    class Config:
        orm_mode = True





class TypeBot(str, Enum):
    prod = "production"
    dev = "develop"
    test = "test"


class BotBase(BaseModel):
    name: str = None


class BotAdd(BotBase):
    token: str = None
    type: TypeBot
    description: str = None
    priority: int = 0


class Bot(BotBase):
    id: int
    proxys: list[Proxy] = []
    # proxy: Union[bool] = False

    class Config:
        orm_mode = True




