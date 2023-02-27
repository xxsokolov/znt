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
from grafana_client import GrafanaApi
from typing import Union

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
                return response.content
            else:
                return False
        except Exception as err:
            self.logger.error("Exception occurred: {}".format(err)), exit(1)


class Grafana:
    def __init__(self, logger):
        self.host = '192.168.1.200'
        self.port = '3000'
        self.proto = 'http'
        self.login = 'admin'
        self.password = 'AdminAdmin'
        self.cookie = None
        self.api_grafana = None
        self.api_dashboard_url = None
        self.logger = logger

    def api_get_dashboard(self, uid) -> Union[bool, str]:
        try:
            self.api_grafana = GrafanaApi.from_url(url="{proto}://{host}:{port}/".format(proto=self.proto,
                                                                                         host=self.host,
                                                                                         port=self.port),
                                                   credential=(self.login, self.password))
            url = self.api_grafana.dashboard.get_dashboard(uid)['meta']['url']
        except Exception as err:
            self.logger.error("Ошибка подключения к Grafana API. \n{}".format(err))
            return False

        else:
            return url

    def get_cookie(self) -> Union[bool, list]:
        try:
            base_url = "{proto}://{host}:{port}/login".format(proto=self.proto, host=self.host, port=self.port)
            data_api = {"user": self.login, "password": self.password}
            req_cookie = requests.post(base_url, json=data_api, verify=False)
        except requests.RequestException as err:
            self.logger.error("Ошибка подключения к Grafana. \n{}".format(err))
            return False
        else:
            self.cookie = []
            for name, value in req_cookie.cookies.items():
                self.cookie.append(dict(name=name, value=value))
            return self.cookie
