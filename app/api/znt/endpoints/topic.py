# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal, engine
from app.api import schemas, models, cruds

models.topic.Base.metadata.create_all(bind=engine)

topic_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@topic_router.get("/topic/", response_model=list[schemas.topic.FullTopic], summary="Показать все топики")
def read_topic(db: Session = Depends(get_db)):
    topic = cruds.topic.get_topic(db)
    if len(topic) == 0:
        raise HTTPException(status_code=404, detail="Список топиков пустой")
    return topic
