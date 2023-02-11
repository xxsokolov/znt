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

import argparse

import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton #, InputMediaPhoto
from classes.argparser import ArgParsing
from config import *
from classes.integration import ZabbixReq
from classes.handlers import ZNT
from classes.telegram import Telegram


import re
import sys
import os
import io
from PIL import Image, ImageDraw, ImageFont
import json
# import yaml
from errno import ENOENT
#import logging

from classes.logger import Log
from classes.parameters import ReadYaml


def watermark_text(img):
    img = io.BytesIO(img)
    img = Image.open(img)
    if img.height < watermark_minimal_height:
        logger.info("Cannot set watermark text, img height {} (min. {})".format(img.height, watermark_minimal_height))
        return False
    font = ImageFont.truetype(watermark_font, 14)

    line_height = sum(font.getmetrics())
    # xxx = font.getbbox(watermark_label)[2]
    # yyy = font.getsize(watermark_label)
    fontimage = Image.new('L', (font.getbbox(watermark_label)[2], line_height))
    ImageDraw.Draw(fontimage).text((0, 0), watermark_label, fill=watermark_fill, font=font)
    fontimage = fontimage.rotate(watermark_rotate,  resample=Image.BICUBIC, expand=True)

    img_size = img.crop().size
    size = (img_size[0]-fontimage.size[0]-5, img_size[1]-fontimage.size[1]-10)

    img.paste(watermark_text_color, box=size, mask=fontimage)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=img.format)
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr


def main():
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
                            send_from='',
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
    elif args.command == 'console':
        #main_config = ReadYaml(logger=logger, args=args).read_yaml()
        send_config = ReadYaml(logger=logger, path=args.SendConfigYaml).read_yaml()
        bot_config = ReadYaml(logger=logger, path=args.BotConfigYaml).read_bots_yaml()
        zabbix_req = ZabbixReq(logger=logger, url=zabbix_api_url, login=zabbix_api_login, password=zabbix_api_pass, chart=zabbix_graph_chart)
        main()

