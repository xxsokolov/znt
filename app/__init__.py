import os
os.environ["APPNAME"] = "ZNT"
os.environ["APPVERSION"] = "2.0"

from configparser import ConfigParser
config = ConfigParser()
config.read("znt.cfg", encoding='utf-8')

from app.classes import logger
logger = logger.Log(debug=True if config.get('logging', 'logging_level') == 'DEBUG' else False)

from fastapi import FastAPI
debug_mode = bool(True if logger.get_level_name() == 'DEBUG' else False)
api_app = FastAPI(
    title='FastAPI: znt', version='2.0', openapi_url='/api/openapi.jsons', docs_url='/api/docs',
    redoc_url='/api/redocs',
    debug=debug_mode
)
