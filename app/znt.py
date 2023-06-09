# -*- coding: utf-8 -*-
####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
__author__ = "Sokolov Dmitry"
__maintainer__ = "Sokolov Dmitry"
__license__ = "MIT"
__appname__ = "ZNT Sender"
__version__ = "2.0"

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fastapi.middleware.wsgi import WSGIMiddleware
from app import config, logger, api_app
import uvicorn
from app.api.v1.api import api_v1_router
# from app.api.v2.api import api_v2_router
from app.api.znt.api import znt_router

if config.getboolean('core', 'adminlte'):
    from app.adminlte.app import create_app

api_app.include_router(api_v1_router, prefix='/api/latest')
api_app.include_router(api_v1_router, prefix='/api/v1')
# app.include_router(api_v2_router, prefix='/api/v2')
api_app.include_router(znt_router, prefix='/api/znt')
if config.getboolean('core', 'adminlte'):
    api_app.mount("/", WSGIMiddleware(create_app()))

if __name__ == "__main__":
    uvicorn.run(app=api_app,
                host=config.get('webserver', 'host'),
                port=int(config.get('webserver', 'port')), log_level=str(logger.get_level_name()).lower(), log_config=None)
