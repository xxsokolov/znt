from typing import Optional, NoReturn

from app import schemas
from app.classes.integration import ZabbixReq
from app.classes.handlers import ZNT
from app.classes.telegram import Telegram

from app.classes.parameters import ReadParam
from app.classes.logger import Log
from app.config.config import *

logger = Log(True).log



async def send_message(json: schemas.SendMessage) -> Optional[NoReturn]:
    send_config = ReadParam(logger=logger, json=json).read_api_mode()
    bot_config = ReadParam(logger=logger, path=r'/app/.bots.yaml').read_bots_yaml()
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
