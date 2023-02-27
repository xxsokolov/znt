from fastapi import APIRouter
from app.api.znt.endpoints.routes import router

znt_router = APIRouter()
znt_router.include_router(router, tags=['/znt'])

