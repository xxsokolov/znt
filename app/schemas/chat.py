from pydantic import BaseModel


class BaseChat(BaseModel):
    name: str
    chat_id_prev: str
    description: str
    type: str


class AddChat(BaseChat):
    chat_id: str = None


class FullChat(BaseChat):
    id: int

    class Config:
        orm_mode = True
