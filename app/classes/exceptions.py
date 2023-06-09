####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import json
from fastapi.encoders import jsonable_encoder
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app import logger, api_app


class ZNTSettingTags(Exception):
    def __init__(self, message, detail):
        self.message = message
        self.detail = detail

    def __str__(self):
        return self.message


class ZNTException(Exception):
    pass


class ZNTAPIException(RequestValidationError):
    @api_app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        print(f"OMG! An HTTP error!: {repr(exc)}")
        return await http_exception_handler(request, exc)

    @api_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.log.error('Ошибка валидации запроса:\n'
                         'Client: {0}:{1}\n'
                         'Headers: {2}\n'
                         'Body: {3}\n'
                         'Error: {4}'.format(request.client.host, request.client.port, request.headers.items(),
                                             json.dumps(exc.body, indent=4), json.dumps(exc.errors(), indent=4)))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )