####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
__author__ = "Sokolov Dmitry"
__maintainer__ = "Sokolov Dmitry"
__license__ = "MIT"
import os
from time import sleep

import grafana_client.client
import requests
from grafana_client import GrafanaApi
from typing import Union
from app import config, logger


class ZabbixReq:

    def __init__(self, url, login, password, chart):
        self.logger = logger.log
        self.url = url
        self.login = login
        self.password = password
        self.chart = chart
        self.grafana_cookie = None

    def get_chart_png(self, itemid, name, period=None):
        attempts = 0
        connect_max_attempts = int(config.get('zabbix', 'connect_max_attempts'))
        connect_timeout = int(config.get('zabbix', 'connect_timeout'))
        self.logger.debug("Подключаемся к Zabbix.")
        while attempts < connect_max_attempts:
            attempts = attempts + 1
            try:
                s = requests.Session()
                s.headers["User-Agent"] = "{}/{}".format(os.environ["APPNAME"], os.environ["APPVERSION"])

                data_api = {"name": self.login, "password": self.password, "enter": "Sign in"}
                req_cookie = s.post(self.url, data=data_api, verify=False, timeout=connect_timeout)
                cookie = req_cookie.cookies
                req_cookie.close()

                response = requests.get(url=config.get('zabbix', 'chart_url').format(
                    name=name,
                    itemid=itemid,
                    zabbix_server=self.url,
                    range_time=period),
                    cookies=cookie,
                    verify=False,
                    timeout=connect_timeout)
            except Exception as err:
                self.logger.error("{}/{}: Ошибка подключения к Zabbix ({}): {}".format(
                    attempts, connect_max_attempts, self.url, err))
                if attempts == connect_max_attempts:
                    return False
                sleep(connect_timeout)
            else:
                return response.content


class Grafana:
    def __init__(self):
        self.host = config.get('grafana', 'host')
        self.port = config.get('grafana', 'port')
        self.proto = config.get('grafana', 'proto')
        self.login = config.get('grafana', 'login')
        self.password = config.get('grafana', 'password')
        self.cookie = None
        self.api_grafana = None
        self.api_dashboard_url = None
        self.logger = logger.log

    def api_get_dashboard(self, uid, panel=None) -> Union[bool, str]:
        attempts = 0
        connect_max_attempts = int(config.get('grafana', 'connect_max_attempts'))
        connect_timeout = int(config.get('grafana', 'connect_timeout'))
        self.logger.debug("Подключаемся к Grafana API.")
        while attempts < connect_max_attempts:
            url = None
            attempts = attempts + 1
            try:
                self.api_grafana = GrafanaApi.from_url(
                    url="{proto}://{host}:{port}/".format(proto=self.proto, host=self.host, port=self.port),
                    credential=(self.login, self.password))
                self.api_grafana.client.timeout = connect_timeout
                self.api_grafana.client.user_agent = "{}/{}".format(os.environ["APPNAME"], os.environ["APPVERSION"])
                if panel:
                    dash = self.api_grafana.dashboard.get_dashboard(uid)
                    if dash:
                        for x in dash['dashboard']['panels']:
                            if x['id'] == int(panel):
                                url = self.api_grafana.dashboard.get_dashboard(uid)['meta']['url'] + '?viewPanel={}'.format(panel)
                                break
                        if not url:
                            self.logger.warn('Панель "{0}" на дашборде {1} Grafana не найдена. Проверьте ид панели и дашборда.'.format(panel, uid))
                            return False
                    else:
                        self.logger.warn('Дашборд {} Grafana не найден.'.format(uid))
                else:
                    url = self.api_grafana.dashboard.get_dashboard(uid)['meta']['url']
            except grafana_client.client.GrafanaException as err:
                self.logger.warn("Ошибка в GrafanaException: {}".format(err))
                return False
            except Exception as err:
                self.logger.error("{}/{}: Ошибка подключения к Grafana API ({}): {}".format(
                    attempts, connect_max_attempts, self.api_grafana.url, err))
                if attempts == connect_max_attempts:
                    return False
                sleep(connect_timeout)
            else:
                self.logger.debug("Получение урл дашборда ({}) выполнено успешно.".format(self.api_grafana.url+url[1:]))
                return url

    def get_cookie(self) -> Union[bool, list]:
        attempts = 0
        connect_max_attempts = int(config.get('grafana', 'connect_max_attempts'))
        connect_timeout = int(config.get('grafana', 'connect_timeout'))
        self.logger.debug("Подключаемся к Grafana для получения cookies.")
        while attempts < connect_max_attempts:
            attempts = attempts + 1
            try:
                base_url = "{proto}://{host}:{port}/login".format(proto=self.proto, host=self.host, port=self.port)
                data_api = {"user": self.login, "password": self.password}
                user_agent = {'User-agent': '{}/{}'.format(os.environ["APPNAME"], os.environ["APPVERSION"])}
                req_cookie = requests.post(base_url, headers=user_agent, json=data_api, verify=False)
            except requests.RequestException as err:
                self.logger.error("Ошибка подключения к Grafana. \n{}".format(err))
                if attempts == connect_max_attempts:
                    return False
                sleep(connect_timeout)
            else:
                self.grafana_cookie = []
                for name, value in req_cookie.cookies.items():
                    self.grafana_cookie.append(dict(name=name, value=value))
                return self.grafana_cookie
