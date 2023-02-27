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

class TypeBot(str, Enum):
    prod = "production"
    dev = "develop"
    test = "test"
class Bot(BaseModel):
    name: str = None
    type: TypeBot
    token: str = None
    description: Union[str, None] = None
    priority: int = 0
    proxy: Union[bool, None] = False

    class Config:
        orm_mode = True




