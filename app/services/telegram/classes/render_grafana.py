# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import os
from time import sleep
from typing import Union

import urllib3
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from app.classes.integration import Grafana
from app import config, logger
import requests.adapters

class RenderingPNG:
    def __init__(self, uid=None, panel=None):
        self.host = config.get('grafana', 'host')
        self.port = config.get('grafana', 'port')
        self.proto = config.get('grafana', 'proto')
        self.logger = logger.log
        self.url: str = Grafana().api_get_dashboard(uid, panel)
        if self.url:
            self.cookie: list = Grafana().get_cookie()

    def get_screenshot(self) -> Union[bool, bytes]:
        attempts = 0
        driver = None
        connect_max_attempts = int(config.get('selenium', 'connect_max_attempts'))
        connect_timeout = int(config.get('selenium', 'connect_timeout'))

        if self.url and self.cookie:
            self.logger.debug("Подключаемся к selenium/standalone-chrome.")
            while attempts < connect_max_attempts:
                attempts = attempts + 1
                try:

                    options = webdriver.ChromeOptions()
                    opt = '''
                    --noerrdialogs --disable-infobars --disable-features 
                    --ignore-certificate-errors --test-type --enable-features=WebUIDarkMode --force-dark-mode 
                    --enable-oop-rasterization --force-gpu-rasterization --enable-native-gpu-memory-buffers 
                    --enable-gpu-rasterization --enable-oop-rasterization-ddl --use-skia-deferred-display-list 
                    --disable-translate'''
                    for x in opt.split():
                        options.add_argument(x)

                    RemoteConnection.set_timeout(connect_timeout)

                    driver = webdriver.Remote(
                        command_executor="http://{host}:{port}/wd/hub".format(
                            host=config.get('selenium', 'host'),
                            port=int(config.get('selenium', 'port'))),
                        desired_capabilities=DesiredCapabilities.CHROME, options=options
                    )

                    driver.get("{proto}://{host}:{port}/login".format(proto=self.proto,
                                                                      host=self.host,
                                                                      port=self.port))
                    for x in self.cookie:
                        driver.add_cookie(x)
                    driver.get('{proto}://{host}:{port}{url}?orgId=1&from=now-3h&kiosk'.format(
                        proto=self.proto, host=self.host, port=self.port, url=self.url))

                except Exception as err:
                    self.logger.error("{}/{}: selenium/standalone-chrome ({}): {}".format(
                        attempts, connect_max_attempts, self.driver.url, err))
                    if attempts == connect_max_attempts:
                        return False
                    sleep(connect_timeout)
                else:
                    try:
                        element = driver.find_element(By.XPATH, "//div[@class='react-grid-layout']")
                        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                        sleep(2)
                        png = element.screenshot_as_png
                    except Exception as err:
                        self.logger.error("Ошибка рендеринга дашборда.\n{}".format(err))
                        return False
                    else:
                        return png
                finally:
                    driver.quit()
        else:
            return False
