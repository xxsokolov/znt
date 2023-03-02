from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import schemas, models, cruds
from app.databases.database import SessionLocal

proxy_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@proxy_router.get("/proxy/", response_model=list[schemas.proxy.FullProxy], summary="Показать все прокси")
def read_proxy(db: Session = Depends(get_db)):
    bots = cruds.proxy.get_proxy(db)
    if len(bots) == 0:
        raise HTTPException(status_code=404, detail="Список прокси пустой")
    return bots
