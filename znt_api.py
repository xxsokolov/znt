from __future__ import annotations
from typing import Callable

import uvicorn
from fastapi import status
from app.classes.logger import Log
from pydantic import BaseModel, Field
from fastapi import Request, Response, HTTPException, APIRouter, FastAPI
from fastapi.routing import APIRoute

from app.config import *
from app.classes.integration import ZabbixReq
from app.classes.handlers import ZNT
from app.classes.telegram import Telegram

from app.classes.parameters import ReadParam

class SendMessage(BaseModel):
    chat_id: str = Field(default=None, description="Укажите @username или Chat Name")
    bot: str = Field(default='default', description="Укажите @username или Chat Name")
    title: str = Field(
        default='Zabbix server - Zabbix server: More than 100 items having missing data for more than 10 minutes',
        description="Укажите @username или Chat Name")
    period: int = Field(default=10800, description="The description of the item")
    header: str = Field(
        default='{Problem} Warning {Warning}: Zabbix server: More than 100C:: items having missing data for more than 10 minutes',
        description="The description of the item")
    body: str = Field(
        default='Host: Zabbix server [127.0.0.1]\nLast value: 0 (12:40:52)\nDuration: 1s\nhost: Zabbix server',
        description="The description of the item")
    hostname: str = Field(default='Zabbix server', description="The description of the item")
    itemid: str = Field(default='23271 *UNKNOWN* *UNKNOWN* *UNKNOWN*', description="The description of the item")
    hostid: str = Field(default='10084', description="The description of the item")
    triggerid: str = Field(default='13486', description="The description of the item")
    triggerurl: str = Field(default='Zabbix server', description="The description of the item")
    eventtags: str = Field(default='target:zabbix, ZNTMentions:@xxsokolov', description="The description of the item")
    eventid: str = Field(default='55', description="The description of the item")
    actionid: str = Field(default='7', description="The description of the item")
    graphs: bool = Field(default=True, description="The description of the item")
    hostlinks: bool = Field(default=True, description="The description of the item")
    graphlinks: bool = Field(default=True, description="The description of the item")
    acklinks: bool = Field(default=True, description="The description of the item")
    eventlinks: bool = Field(default=True, description="The description of the item")
    triggerlinks: bool = Field(default=True, description="The description of the item")
    eventtag: bool = Field(default=True, description="The description of the item")
    eventidtag: bool = Field(default=True, description="The description of the item")
    itemidtag: bool = Field(default=True, description="The description of the item")
    triggeridtag: bool = Field(default=True, description="The description of the item")
    actionidtag: bool = Field(default=True, description="The description of the item")
    hostidtag: bool = Field(default=True, description="The description of the item")
    zntsettingstag: bool = Field(default=True, description="The description of the item")
    zntmentions: bool = Field(default=True, description="The description of the item")
    keyboard: bool = Field(default=True, description="The description of the item")
    graphs_period: str = Field(default='default', description="The description of the item")




class RouteErrorHandler(APIRoute):
    """Custom APIRoute that handles application errors and exceptions"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as ex:
                if isinstance(ex, HTTPException):
                    raise ex
                logger.exception("uncaught error")
                # wrap error into pretty 500 exception
                raise HTTPException(status_code=500, detail=str(ex))

        return custom_route_handler


router = APIRouter(route_class=RouteErrorHandler)
api = FastAPI(debug=True)
v1 = FastAPI(debug=True)
api.mount("/api/v1", v1)
api.include_router(router)
logger = Log(True).log


def run(host="0.0.0.0", port=8000):
    return uvicorn.run(api, host=host, port=port)


@v1.post("/telegram/sendMessage", status_code=status.HTTP_202_ACCEPTED, summary="Send message in Telegram")
def send_message(data: SendMessage):
    xxx = {'preferences': {
        "telegram":
            {"send":
                 {"bot": data.bot,
                  "chat_id": data.chat_id,
                  "charts": {
                      "title": data.title,
                      "period": data.period},
                  "message": {
                      "header": data.header,
                      "body": data.body}}},
        "zabbix":
            {"macros":
                 {"hostname": data.hostname, "itemid": data.itemid, "hostid": data.hostid, "triggerid": data.triggerid,
                  "triggerurl": data.triggerurl, "eventtags": data.eventtags, "eventid": data.eventid,
                  "actionid": data.actionid}},
        "znt":
            {"options":
                 {"graphs": data.graphs, "hostlinks": data.hostlinks, "graphlinks": data.graphlinks,
                  "acklinks": data.acklinks, "eventlinks": data.eventlinks, "triggerlinks": data.triggerlinks,
                  "eventtag": data.eventtag, "eventidtag": data.eventidtag, "itemidtag": data.itemidtag,
                  "triggeridtag": data.triggeridtag, "actionidtag": data.actionidtag, "hostidtag": data.hostidtag,
                  "zntsettingstag": data.zntsettingstag, "zntmentions": data.zntmentions, "keyboard": data.keyboard,
                  "graphs_period": data.graphs_period}}}}
    # yyy = None
    # ttt = logger.__dict__
    try:
        telegram(SendConfigYaml=xxx)
    except Exception as err:
        return dict(state='Error')
    else:
        return dict(state='Ok')
    finally:
        return dict(state='Ok')


@v1.get("/telegram/sendMessage", status_code=status.HTTP_200_OK)
def get_example():
    return dict(state='Ok', example=SendMessage.construct())


def telegram(SendConfigYaml):
    graph_period = None
    graph_period_raw = None
    send_config = ReadParam(logger=logger, json=SendConfigYaml).read_api_mode()
    bot_config = ReadParam(logger=logger, path='app/.bots.yaml').read_bots_yaml()
    zabbix_req = ZabbixReq(logger=logger, url=zabbix_api_url, login=zabbix_api_login, password=zabbix_api_pass,
                           chart=zabbix_graph_chart)
    logger.info("Send to '{}' action: '{}'".format(send_config.preferences.telegram.send.chat_id, send_config.preferences.telegram.send.message.header))

    znt = ZNT(logger=logger, bots=bot_config, zabbix_req=zabbix_req,  preferences=send_config.preferences)

    xxx = Telegram(token=znt.bot,
                            proxy=znt.proxy,
                            send_to=send_config.preferences.telegram.send.chat_id,
                            message=znt.message,
                            keyboard=send_config.preferences.znt.options.keyboard,
                            chart_png=znt.chart_png,
                            disable_notification=znt.settings_not_notify,
                            logger=logger)
    return xxx



