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

models.proxy.Base.metadata.create_all(bind=engine)

proxy_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@proxy_router.get("/proxy/", response_model=list[schemas.proxy.FullProxy], summary="Показать все прокси")
def read_proxy(db: Session = Depends(get_db)):
    proxy = cruds.proxy.get_proxy(db)
    if len(proxy) == 0:
        raise HTTPException(status_code=404, detail="Список прокси пустой")
    return proxy
