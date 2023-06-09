# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import json
import traceback

from fastapi import Depends, HTTPException, APIRouter, status, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union

from app.databases.database import SessionLocal
from app.services.telegram.send import send_message
from app.api import schemas, models
from app.classes.exceptions import *
from app import logger
telegram_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@telegram_router.post("/telegram/sendMessage", status_code=status.HTTP_200_OK, response_model=schemas.telegram.ZabbixTPDA,
                      summary="Отправить сообщение в Telegram")
async def telegram_send_message(request: Request,
                          parameters: Union[schemas.telegram.ZabbixTPDA, schemas.telegram.ZabbixService] = Body(...),
                          db: Session = Depends(get_db)):
    try:
        json_ = await request.json()
    except json.decoder.JSONDecodeError:
        json_ = None

    logger.log.debug('Получен запрос:\n'
                     'Client: {0}:{1}\n'
                     'Headers: {2}\n'
                     'Body: {3}'.format(request.client.host, request.client.port, request.headers.items(),
                                        json.dumps(json_, indent=4)))

    bots = db.query(models.bot.Bot).outerjoin(models.proxy.Proxy, models.bot.Bot.proxy_id == models.proxy.Proxy.id).all()
    bot_list = []
    for bot in bots:
        proxy_dict = {}
        bot_dict = {column.name: getattr(bot, column.name) for column in bot.__table__.columns}
        if bot_dict['proxy_id']:
            proxy_dict = {column.name: getattr(bot.proxy, column.name) for column in bot.proxy.__table__.columns}
        bot_dict['proxy'] = proxy_dict
        bot_list.append(bot_dict)

    send_config = None
    body = parameters.dict()
    if isinstance(parameters, schemas.telegram.ZabbixTPDA):
        send_config = dict(
            preferences=dict(
                telegram=dict(
                    send=dict(
                        bot=body['bot'], bot_group=body['bot_group'], send_to=body['send_to'],
                        charts=dict(title=body['title'], period=body['period']), message=dict(header=body['header'],
                                                                                              body=body['body']))),
                zabbix=dict(
                    macros=dict(hostname=body['hostname'], itemid=body['itemid'], hostid=body['hostid'],
                                triggerid=body['triggerid'], triggerurl=body['triggerurl'],
                                eventtags=body['eventtags'],
                                eventid=body['eventid'], actionid=body['actionid'])),
                znt=dict(
                    options=dict(
                        graphs=body['graphs'], hostlinks=body['hostlinks'], graphlinks=body['graphlinks'],
                        acklinks=body['acklinks'], eventlinks=body['eventlinks'], triggerlinks=body['triggerlinks'],
                        eventtag=body['eventtag'], eventidtag=body['eventidtag'], itemidtag=body['itemidtag'],
                        triggeridtag=body['triggeridtag'], actionidtag=body['actionidtag'],
                        hostidtag=body['hostidtag'],
                        zntsettingstag=body['zntsettingstag'], zntmentions=body['zntmentions'],
                        keyboard=body['keyboard'],
                        graphs_period=body['graphs_period']
                    )
                )
            )
        )
    elif isinstance(parameters, schemas.telegram.ZabbixService):
        send_config = dict(
            preferences=dict(
                telegram=dict(
                    send=dict(
                        bot=body['bot'], bot_group=body['bot_group'], send_to=body['send_to'],
                        charts=dict(title='', period=''), message=dict(header=body['header'], body=body['body']))),
                zabbix=dict(
                    macros=dict(hostname='', itemid='', hostid='',
                                triggerid='', triggerurl='', eventtags=body['eventtags'],
                                eventid='', actionid='')),
                znt=dict(
                    options=dict(
                        graphs=False, hostlinks=False, graphlinks=False,
                        acklinks=False, eventlinks=False, triggerlinks=False,
                        eventtag=body['eventtag'], eventidtag=False, itemidtag=False,
                        triggeridtag=False, actionidtag=False, hostidtag=False,
                        zntsettingstag=body['zntsettingstag'], zntmentions=body['zntmentions'], keyboard=body['keyboard'],
                        graphs_period=0
                    )
                )
            )
        )
    try:

        response = send_message(bot_config=bot_list, send_config=send_config)
    except ZNTSettingTags as err:
        return JSONResponse(content=dict(status=dict(message=err.message, detail=err.detail)))
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail={"type": type(err).__name__, "error": str(err), "at": str(traceback.format_exc())},
                            headers={"X-Error": "ERROR"})
    else:
        return JSONResponse(
            content=dict(status="Собщение отправлено",
                         request={**send_config},
                         response={**dict(response=response.response_tg_json)}),
            status_code=200
        )
