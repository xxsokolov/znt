# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy.orm import Session
from app.api import schemas, models


def find_bot(db: Session, bot_id: int = None, name: str = None):
    if bot_id:
        return db.query(models.bot.Bot).filter(models.bot.Bot.id == bot_id).all()
    elif name:
        return db.query(models.bot.Bot).filter(models.bot.Bot.name == name).all()
    else:
        return db.query(models.bot.Bot).all()


def add_bot(db: Session, bot: schemas.bot.AddBot):
    db_bot = models.bot.Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


def delete_bot(db: Session, bot_id: int):
    db.query(models.bot.Bot).filter(models.bot.Bot.id == bot_id).delete()
    db.commit()
    return {"ok": True}
