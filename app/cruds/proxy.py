from sqlalchemy.orm import Session

from app import schemas, models
# from app.models import proxy


def get_proxy(db: Session):
    return db.query(models.proxy.Proxy).all()
