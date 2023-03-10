# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import traceback

from .classes.integration import ZabbixReq
from .classes.handlers import ZNT
from .classes.telegram import Telegram

from .classes.parameters import ReadParam
from .classes.logger import Log
from app.services.telegram.config import *

logger = Log(True).log


def send_message(bot_config, send_config):
    try:
        # bot_config = ReadParam(logger=logger, json=bot_config).read_api_mode()
        send_config = ReadParam(logger=logger, json=send_config).read_api_mode()
        # bot_config = ReadParam(logger=logger, path=r'/app/.bots.yaml').read_bots_yaml()
        zabbix_req = ZabbixReq(logger=logger, url=zabbix_api_url, login=zabbix_api_login, password=zabbix_api_pass,
                               chart=zabbix_graph_chart)
        # logger.info("Send to '{}' action: '{}'".format(send_config.preferences.telegram.send.chat_id, send_config.preferences.telegram.send.message.header))

        znt = ZNT(logger=logger, bots=bot_config, zabbix_req=zabbix_req,  preferences=send_config.preferences)

        xx = Telegram(token=znt.bot_token,
                       send_to=send_config.preferences.telegram.send.chat_id,
                       message=znt.message,
                       keyboard=send_config.preferences.znt.options.keyboard,
                       chart_png=znt.chart_png,
                       disable_notification=znt.settings_not_notify,
                       proxy=znt.bot_proxy,
                       proxy_use=znt.bot_proxy_use,
                       logger=logger)
    except Exception as err:
        print(traceback.print_exc())
        raise err
    else:
        return xx