# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from fastapi import APIRouter, status

healthcheck_router = APIRouter()


@healthcheck_router.get("/healthcheck", status_code=status.HTTP_200_OK, summary="Состояние сервиса")
async def healthcheck():
    return {"status": "ok"}
