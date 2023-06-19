# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import APIRouter
from app.api.v1.endpoints.telergam import telegram_router

api_v1_router = APIRouter()
api_v1_router.include_router(telegram_router, tags=['telegram'])
