from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_bots(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bot).offset(skip).limit(limit).all()

def get_bot_by_name(db: Session, name: str):
    return db.query(models.Bot).filter(models.Bot.name == name).first()

def add_bot(db: Session, bot: schemas.Bot):
    db_bot = models.Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
