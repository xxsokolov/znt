from sqlalchemy.orm import Session

from app import models


def get_chat(db: Session):
    return db.query(models.chat.Chat).all()
