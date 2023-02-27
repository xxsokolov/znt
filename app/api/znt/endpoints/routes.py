from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/bot/", response_model=list[schemas.Bot], summary="Показать всех ботов")
def read_users(db: Session = Depends(get_db)):
    bots = crud.get_bots(db)
    if len(bots) == 0:
        raise HTTPException(status_code=404, detail="Список ботов пустой")
    return bots

@router.post("/bot/", response_model=schemas.Bot, summary="Добавить бота")
def add_bot(bot: schemas.Bot, db: Session = Depends(get_db),
            ):
    if crud.get_bot_by_name(db, name=bot.name):
        raise HTTPException(status_code=400, detail="Бот {bot.name} уже существует".format(bot=bot))
    crud.add_bot(db, bot)
    return JSONResponse(content={"status": "Бот {name} создан".format(**bot.dict()), "detail": bot.dict()})


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@router.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
