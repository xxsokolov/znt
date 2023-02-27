#!/usr/lib/zabbix/alertscripts/venv/bin/python
# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
__author__ = "Sokolov Dmitry"
__maintainer__ = "Sokolov Dmitry"
__license__ = "MIT"
from app.classes.argparser import ArgParsing
from app.config import *
from app.classes.integration import ZabbixReq
from app.classes.handlers import ZNT
from app.classes.telegram import Telegram
import znt_api as api

import sys
from app.classes.logger import Log
from app.classes.parameters import ReadParam


def telegram():
    graph_period = None
    graph_period_raw = None
    logger.info("Send to '{}' action: '{}'".format(args.Username, send_config.preferences.telegram.send.message.header))
    # logger.debug("sys.argv: {}".format(sys.argv[1:]))
    # logger.debug("Send to {}\naction: {}\nxml: {}".format(args.username,
    #                                                       send_config.preferences.telegram.send.message.header,
    #                                                       send_config.__dict__))

    znt = ZNT(logger=logger, bots=bot_config, zabbix_req=zabbix_req,  preferences=send_config.preferences)

    send_message = Telegram(token=znt.bot,
                            proxy=znt.proxy,
                            send_to=args.Username,
                            message=znt.message,
                            keyboard=send_config.preferences.znt.options.keyboard,
                            chart_png=znt.chart_png,
                            disable_notification=znt.settings_not_notify,
                            logger=logger)


if __name__ == "__main__":
    args = ArgParsing()
    args = args.create_parser().parse_args(sys.argv[1:])
    logger = Log(False if not args.debug else True).log
    if args.command == 'zabbix':
        pass
    elif args.command == 'api':
        api.run()
    elif args.command == 'console':
        send_config = ReadParam(logger=logger, path=args.SendConfigYaml).read_yaml()
        bot_config = ReadParam(logger=logger, path=args.BotConfigYaml).read_bots_yaml()
        zabbix_req = ZabbixReq(logger=logger, url=zabbix_api_url, login=zabbix_api_login, password=zabbix_api_pass, chart=zabbix_graph_chart)
        telegram()
# @app.get("send")
#main_config = ReadYaml(logger=logger, args=args).read_yaml()

