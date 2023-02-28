from fastapi import APIRouter
from app.api.znt.endpoints.bot import bot_router
from app.api.znt.endpoints.proxy import proxy_router

znt_router = APIRouter()

znt_router.include_router(bot_router, tags=['znt.bot'])
znt_router.include_router(proxy_router, tags=['znt.proxy'])