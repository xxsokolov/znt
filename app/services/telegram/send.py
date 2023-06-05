# -*- coding: utf-8 -*-
####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import traceback

from app.classes.integration import ZabbixReq
from .classes.handlers import ZNT
from .classes.telegram import Telegram

from .classes.parameters import ReadParam
from app import config, logger


def send_message(bot_config, send_config):
    try:
        send_config = ReadParam(json=send_config).read_api_mode()
        zabbix_req = ZabbixReq(url=config.get('zabbix', 'url'),
                               login=config.get('zabbix', 'login'),
                               password=config.get('zabbix', 'password'),
                               chart=config.get('zabbix', 'chart_url'))

        znt = ZNT(bots=bot_config, zabbix_req=zabbix_req, preferences=send_config.preferences)

        response = Telegram(token=znt.bot_token,
                            send_to=send_config.preferences.telegram.send.send_to,
                            # topic=send_config.preferences.telegram.send.topic,
                            message=znt.message,
                            keyboard=send_config.preferences.znt.options.keyboard,
                            chart_png=znt.chart_png,
                            disable_notification=znt.settings_not_notify,
                            proxy=znt.bot_proxy,
                            proxy_use=znt.bot_proxy_use)
    except Exception as err:
        # logger.log.error(err, exc_info=config.getboolean('logging', 'exc_info'))
        raise err
    else:
        return response
