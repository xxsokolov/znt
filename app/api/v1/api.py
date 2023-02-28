from fastapi import APIRouter
from app.api.v1.endpoints.telergam import router

api_v1_router = APIRouter()
api_v1_router.include_router(router, tags=['/api/v1'])
