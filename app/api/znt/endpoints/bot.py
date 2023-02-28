from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.models import models
from app.cruds import crud
from app.databases.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

bot_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@bot_router.get("/bot/", response_model=list[schemas.Bot], summary="Показать всех ботов")
def read_users(db: Session = Depends(get_db)):
    bots = crud.get_bots(db)
    if len(bots) == 0:
        raise HTTPException(status_code=404, detail="Список ботов пустой")
    return bots

@bot_router.post("/bot/", response_model=schemas.Bot, summary="Добавить бота")
def add_bot(bot: schemas.BotAdd, db: Session = Depends(get_db),
            ):
    if crud.get_bot_by_name(db, name=bot.name):
        raise HTTPException(status_code=400, detail="Бот {bot.name} уже существует".format(bot=bot))
    crud.add_bot(db, bot)
    return JSONResponse(content={"status": "Бот {name} создан".format(**bot.dict()), "detail": bot.dict()})


@bot_router.get("/bot/{name}", response_model=schemas.Bot, summary="Найти бота по имени")
def read_bot(name: str, db: Session = Depends(get_db)):
    db_user = crud.get_bot_by_name(db, name=name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Бот не найден")
    return db_user
