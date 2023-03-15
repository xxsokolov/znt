# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy.orm import Session
from app.api import schemas, models

def get_bots(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.bot.Bot).offset(skip).limit(limit).all()


def get_bot_by_name(db: Session, name: str):
    return db.query(models.bot.Bot).filter(models.bot.Bot.name == name).first()


def add_bot(db: Session, bot: schemas.bot.AddBot):
    db_bot = models.bot.Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

