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
import requests
import urllib3
from config import *


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ZabbixReq:

    def __init__(self, logger, url, login, password, chart):
        self.logger = logger
        self.url = url
        self.login = login
        self.password = password
        self.chart = chart
        self.cookie = None

    def __get_cookie(self):
        data_api = {"name": self.login, "password": self.password, "enter": "Sign in"}
        req_cookie = requests.post(self.url, data=data_api, verify=False)
        self.cookie = req_cookie.cookies
        req_cookie.close()
        if not any(_ in self.cookie for _ in ['zbx_session', 'zbx_sessionid']):
            self.logger.error(
                'User authorization failed: {} ({})'.format('Login name or password is incorrect.', self.url))
            return False
        return self.cookie

    def get_chart_png(self, itemid, name, period=None):
        try:
            if self.__get_cookie():
                response = requests.get(zabbix_graph_chart.format(
                    name=name,
                    itemid=itemid,
                    zabbix_server=self.url,
                    range_time=period),
                    cookies=self.cookie,
                    verify=False)

                # if watermark:
                #     wmt = watermark_text(response.content)
                #     if wmt:
                #         return dict(img=wmt, url=response.url)
                #     else:
                #         return dict(img=response.content, url=response.url)
                # else:
                #
                return dict(img=response.content, url=response.url)
            else:
                return dict(img=None, url=None)
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err)), exit(1)
