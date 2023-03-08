# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app import schemas, models, cruds
from app.databases.database import SessionLocal, engine

models.chat.Base.metadata.create_all(bind=engine)

chat_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@chat_router.get("/chat/", response_model=list[schemas.chat.FullChat], summary="Показать все чаты")
def read_chat(db: Session = Depends(get_db)):
    chat = cruds.chat.get_chat(db)
    if len(chat) == 0:
        raise HTTPException(status_code=404, detail="Список чатов пустой")
    return chat
