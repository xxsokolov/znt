# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from classes.integration import Grafana


class RenderingPNG:
    def __init__(self, uid):
        self.host = '192.168.1.200'
        self.port = '3000'
        self.proto = 'http'
        self.width = 1050
        self.height = 500
        self.timeout_render = 5
        self.url: str = Grafana().api_get_dashboard(uid)
        self.cookie: dict = Grafana().get_cookie()

    def get_screenshote(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--kiosk")
        options.add_argument("--disable-extensions")
        driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\xxsok\PycharmProjects\znt\files\bdriver\yandexdriver.exe')
        driver.get("{proto}://{host}:{port}/login".format(proto=self.proto,
                                                          host=self.host,
                                                          port=self.port))
        for x in self.cookie:
            driver.add_cookie(x)
        driver.get('{proto}://{host}:{port}{url}?orgId=1&from=now-3h&viewPanel=2&kiosk'.format(
            proto=self.proto, host=self.host, port=self.port, url=self.url))
        # driver.quit()
        driver.set_window_position(0, 0)
        driver.set_window_size(self.width, self.height)

        title = driver.title
        png = driver.get_screenshot_as_png()
        driver.quit()
        return dict(img=png, title=title)
