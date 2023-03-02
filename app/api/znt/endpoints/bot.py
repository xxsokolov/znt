from fastapi import Depends, HTTPException, APIRouter, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union, Optional, List

from app import schemas, models, cruds
from app.databases.database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)

bot_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@bot_router.get("/bot/", response_model=list[schemas.bot.FullBot], summary="Показать всех ботов")
def get_bots(db: Session = Depends(get_db)):
    bots = cruds.bot.get_bots(db)
    if len(bots) == 0:
        raise HTTPException(status_code=404, detail="Список ботов пустой")
    return bots

@bot_router.post("/bot/", response_model=schemas.bot.FullBot, summary="Добавить бота")
def add_bot(bot: schemas.bot.AddBot, db: Session = Depends(get_db)):
    if cruds.bot.get_bot_by_name(db, name=bot.name):
        raise HTTPException(status_code=400, detail="Бот {bot.name} уже существует".format(bot=bot))
    cruds.bot.add_bot(db, bot)
    return JSONResponse(content={"status": "Бот {name} добавлен".format(**bot.dict()), "detail": bot.dict()})


@bot_router.get("/bot/{name}", response_model=schemas.bot.FullBot,  summary="Найти бота по имени")
def get_bot_by_name(
        name: str = Path(..., example='@test_bot', description="Укажите имя бота.", regex="^(?=.{5,35}$)@[a-zA-Z0-9_]+(?:bot|Bot)"),
        db: Session = Depends(get_db)):
    db_user = cruds.bot.get_bot_by_name(db, name=name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Бот не найден")
    return db_user
