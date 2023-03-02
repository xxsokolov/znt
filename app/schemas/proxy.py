from typing import Union, Optional, List
from pydantic import BaseModel, Field


class BaseProxy(BaseModel):
    proto: str
    url: str
    description: Union[str, None] = None


class FullProxy(BaseProxy):
    id: int

    class Config:
        orm_mode = True
