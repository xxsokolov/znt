import os
import sys
from dotenv import load_dotenv

load_dotenv()
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from app.api.v1.api import api_v1_router
# from app.api.v2.api import api_v2_router
from app.api.znt.api import znt_router
from fastapi import FastAPI

debug_mode = bool(True if os.environ.get("DEBUG") == 'True' else False)

app = FastAPI(
    title='FastAPI: znt', version='2.0', debug=debug_mode
)
app.include_router(api_v1_router, prefix='/api/latest')
app.include_router(api_v1_router, prefix='/api/v1')
app.include_router(znt_router, prefix='/api/znt')
# app.include_router(api_v2_router, prefix='/api/v2')

