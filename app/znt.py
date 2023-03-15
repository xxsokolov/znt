# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import os
import sys
from dotenv import load_dotenv
import uvicorn

load_dotenv()
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from app.api.v1.api import api_v1_router
# from app.api.v2.api import api_v2_router
from app.api.znt.api import znt_router
from app.admin.admin import flask_admin_app


from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
# from flask import Flask, render_template

debug_mode = bool(True if os.environ.get("DEBUG") == 'True' else False)

api_app = FastAPI(
    title='FastAPI: znt', version='2.0', openapi_url='/api/openapi.jsons', docs_url='/api/docs', redoc_url='/api/redocs',
    debug=debug_mode
)

api_app.mount("/admin", WSGIMiddleware(flask_admin_app))
api_app.include_router(api_v1_router, prefix='/api/latest')
api_app.include_router(api_v1_router, prefix='/api/v1')
api_app.include_router(znt_router, prefix='/api/znt')
# app.include_router(api_v2_router, prefix='/api/v2')


if __name__ == "__main__":
    uvicorn.run(app=api_app, host=os.environ.get("UVICORN_BIND_ADDRESS"), port=int(os.environ.get("UVICORN_BIND_PORT")))
