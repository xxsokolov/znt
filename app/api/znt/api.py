# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import APIRouter
from app.api.znt.endpoints.bot import bot_router
from app.api.znt.endpoints.proxy import proxy_router
from app.api.znt.endpoints.chat import chat_router

znt_router = APIRouter()

znt_router.include_router(bot_router, tags=['znt.bot'])
znt_router.include_router(proxy_router, tags=['znt.proxy'])
znt_router.include_router(chat_router, tags=['znt.chat'])
