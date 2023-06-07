# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import json
import traceback

from fastapi import Depends, HTTPException, APIRouter, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

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


@telegram_router.post("/telegram/sendMessage", status_code=status.HTTP_200_OK, response_model=schemas.telegram.Message,
                      summary="Отправить сообщение в Telegram")
async def telegram_send_message(request: Request, schema: schemas.telegram.Message, db: Session = Depends(get_db)):
    msg = schema.dict()
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
    if msg['media_type'] == 'TPDA':
        send_config = {'preferences': {
            "telegram":
                {"send":
                     {"bot": msg['bot'],
                      "bot_group": msg['bot_group'],
                      "send_to": msg['send_to'],
                      "charts": {
                          "title": msg['title'],
                          "period": msg['period']},
                      "message": {
                          "header": msg['header'],
                          "body": msg['body']}}},
            "zabbix":
                {"macros":
                     {"hostname": msg['hostname'], "itemid": msg['itemid'], "hostid": msg['hostid'], "triggerid": msg['triggerid'],
                      "triggerurl": msg['triggerurl'], "eventtags": msg['eventtags'], "eventid": msg['eventid'],
                      "actionid": msg['actionid']}},
            "znt":
                {"options":
                     {"graphs": msg['graphs'], "hostlinks": msg['hostlinks'], "graphlinks": msg['graphlinks'],
                      "acklinks": msg['acklinks'], "eventlinks": msg['eventlinks'], "triggerlinks": msg['triggerlinks'],
                      "eventtag": msg['eventtag'], "eventidtag": msg['eventidtag'], "itemidtag": msg['itemidtag'],
                      "triggeridtag": msg['triggeridtag'], "actionidtag": msg['actionidtag'], "hostidtag": msg['hostidtag'],
                      "zntsettingstag": msg['zntsettingstag'], "zntmentions": msg['zntmentions'], "keyboard": msg['keyboard'],
                      "graphs_period": msg['graphs_period']}}}}
    try:
        try:
            json_ = await request.json()
        except json.decoder.JSONDecodeError:
            json_ = None

        logger.log.debug('Получен запрос:\n'
                         'Client: {0}:{1}\n'
                         'Headers: {2}\n'
                         'Body: {3}'.format(request.client.host, request.client.port, request.headers.items(),
                                            json.dumps(json_, indent=4)))
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
