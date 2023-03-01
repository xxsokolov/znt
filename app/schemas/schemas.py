from typing import Union, Optional, List

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
    proto: str
    url: str
    description: Union[str, None] = None


# class ProxyAdd(ProxyBase):
#     pass

from pydantic import validator
class Proxy(ProxyBase):
    id: int

    # @validator('id', pre=True)
    # def _iter_to_list(cls, v):
    #     return v
    class Config:
        orm_mode = True



class TypeBot(str, Enum):
    prod = "production"
    dev = "develop"
    test = "test"


class BotBase(BaseModel):
    id: int
    name: str = None
    description: str = None
    type: TypeBot
    priority: int = 0


class BotAdd(BotBase):
    token: str = None


class Bot(BotBase):
    proxy_use: bool = False
    #proxy_id: Union[int, None] = None
    proxy: Proxy = None
    # @validator('proxy', pre=True)
    # def _iter_to_list(cls, v):
    #     return v
    class Config:
        orm_mode = True





