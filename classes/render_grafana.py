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


class RenderingPNG:
    def __init__(self):
        base_url = "http://192.168.1.200:3000/login"
        data_api = {"user": "admin", "password": "AdminAdmin"}
        req_cookie = requests.post(base_url, json=data_api, verify=False)
        self.cookie = []

        for name, value in req_cookie.cookies.items():
            self.cookie.append(dict(name=name, value=value))


        req_cookie.close()

    def get_screenshote(self, url, login, password, width, height, timeout_render):
        options = Options()
        options.headless = True
        options.add_argument("-kiosk")
        driver = webdriver.Chrome(options=webdriver.ChromeOptions(), executable_path=r'C:\Users\xxsok\PycharmProjects\znt\files\bdriver\yandexdriver.exe')
        driver.get('http://192.168.1.200:3000/')
        for x in self.cookie:
            driver.add_cookie(x)
        driver.get('http://192.168.1.200:3000/d/YGLp1d14k/test_dash?orgId=1&from=now-3h&viewPanel=2&kiosk')
        driver.set_window_position(0, 0)
        driver.set_window_size(width, height)

        # time.sleep(timeout_render)
        title = driver.title
        png = driver.get_screenshot_as_png()
        driver.quit()
        return dict(img=png, title=title)
