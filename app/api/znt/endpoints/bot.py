# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from typing import Union
from fastapi import Depends, HTTPException, APIRouter, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.databases.database import SessionLocal, engine
from app.api import schemas, models, cruds

models.bot.Base.metadata.create_all(bind=engine)

bot_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@bot_router.get("/bot/", response_model=list[schemas.bot.FullBot], summary="Найти бота")
def find_bot(
        id: Union[int, None] = None,
        name: Union[str, None] = Query(None, regex="^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)"),
        db: Session = Depends(get_db)) -> list[list]:
    find_bot = cruds.bot.find_bot(db, bot_id=id, name=name)
    if find_bot is None:
        raise HTTPException(status_code=404, detail="Бот {bot} не найден".format(bot=name))
    return find_bot


@bot_router.post("/bot/add", response_model=schemas.bot.FullBot, summary="Добавить бота")
def add_bot(bot: schemas.bot.AddBot, db: Session = Depends(get_db)):
    if cruds.bot.find_bot(db, name=bot.name):
        raise HTTPException(status_code=400, detail="Бот {bot.name} уже существует".format(bot=bot))
    cruds.bot.add_bot(db, bot)
    return JSONResponse(content={"status": "Бот {name} добавлен".format(**bot.dict()), "detail": bot.dict()})


@bot_router.delete("/bot/{id}", response_model=schemas.bot.FullBot, summary="Удалить бота")
def delete_bot_by_id(
        id: int = Path(..., example='1', description="Укажите ид бота."),
        db: Session = Depends(get_db)):
    get_bot_id = cruds.bot.find_bot(db, bot_id=id)
    if get_bot_id is None:
        raise HTTPException(status_code=404, detail="Бот с ид {id} не найден".format(id=id))
    cruds.bot.delete_bot(db, bot_id=id)
    return JSONResponse(content={"status": "Бот {name} ({id}) удален".format(**get_bot_id.__dict__)})
