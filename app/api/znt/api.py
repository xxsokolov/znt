from fastapi import APIRouter
from app.api.znt.endpoints.routes import router
from app.api.znt.config import database

znt_router = APIRouter()
znt_router.include_router(router, tags=['/znt'])


''' APP EVENT SETTING'''
@znt_router.on_event("startup")
async def startup():
    await database.connect()


@znt_router.on_event("shutdown")
async def shutdown():
    await database.disconnect()
