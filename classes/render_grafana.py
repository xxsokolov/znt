# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import time
from typing import Union

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from classes.integration import Grafana


class RenderingPNG:
    def __init__(self, uid, logger):
        self.host = '192.168.1.200'
        self.port = '3000'
        self.proto = 'http'
        self.width = 1050
        self.height = 500
        self.timeout_render = 5
        self.logger = logger
        self.url: str = Grafana(self.logger).api_get_dashboard(uid)
        if self.url:
            self.cookie: list = Grafana(self.logger).get_cookie()

    def get_screenshot(self) -> Union[bool, bytes]:
        if self.url and self.cookie:
            options = webdriver.ChromeOptions()
            opt = '''
            --noerrdialogs --disable-infobars --disable-features 
            --ignore-certificate-errors --test-type --enable-features=WebUIDarkMode --force-dark-mode 
            --enable-oop-rasterization --force-gpu-rasterization --enable-native-gpu-memory-buffers 
            --enable-gpu-rasterization --enable-oop-rasterization-ddl --use-skia-deferred-display-list 
            --disable-translate'''
            for x in opt.split():
                options.add_argument(x)
            driver = webdriver.Remote("http://znt_firefox:4444/wd/hub", DesiredCapabilities.FIREFOX)
            driver.get("{proto}://{host}:{port}/login".format(proto=self.proto,
                                                              host=self.host,
                                                              port=self.port))
            for x in self.cookie:
                driver.add_cookie(x)
            driver.get('{proto}://{host}:{port}{url}?orgId=1&from=now-3h&kiosk'.format(
                proto=self.proto, host=self.host, port=self.port, url=self.url))

            try:
                element = driver.find_element(By.XPATH, "//div[@class='react-grid-layout']")
                WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                time.sleep(2)
                png = element.screenshot_as_png
            except Exception as err:
                print("Ошибка рендеринга дашборда.\n{}".format(err))
                return False
            else:
                return png
            finally:
                driver.quit()
        else:
            return False


        # element = driver.find_element(By.XPATH, "//div[@class='react-grid-layout']")
        # x = driver.execute_script("return document.readyState")
        # element.screenshot(r'C:\Users\xxsok\PycharmProjects\znt\files\test.png')
        # title = driver.title
        # png = driver.get_screenshot_as_png()
        #
        # driver.quit()
        # return dict(img=element, title=title)
        #
        # element = driver.find_element(By.XPATH, "//div[@class='react-grid-layout']")
        # driver.set_window_position(0, 0)
        # driver.set_window_rect(width=1050, height=500)
        # # x = element.size['height']
        # y = driver.get_window_size().get('height')
        # # b = driver.execute_script("return document.body.scrollHeight")
        # # a = b + y
        # while element.size['height'] != 0:  # this will scroll 3 times
        #     y += 100
        #     # fff = element.size['height']
        #     # vvv = driver.execute_script("return document.body.scrollHeight")
        #     driver.set_window_rect(width=1050, height=y)
        #     # x = element.size['height']
        #     # y = driver.get_window_size().get('height')
        #
        #
        #
        #
        # driver.set_window_position(0, 0)
        # driver.set_window_rect(width=1050, height=100)
        # driver.set_window_rect(width=1100, height=200)
        # driver.set_window_rect(width=1200, height=300)
        # x = element.size['height']
        # y = driver.get_window_size().get('height')
        # a = driver.execute_script("return document.body.scrollHeight")
        # x1 = element.size['height']
        # y1 = driver.get_window_size().get('height')
        # x2 = element.size['height']
        # y2 = driver.get_window_size().get('height')
        # y4 = element.size['height']
        # y3 = driver.get_window_size().get('height')
        # y3 = element.size['height']
        #
        #
        # x1 = element.size['height']
        # y1 = driver.get_window_size().get('height')
        #
        # a = x+y
        # b = (x+y) / 100 * 11
        # c = a - b
        #
        # print('{:.2f}'.format(x1+y1-(x1+y1) / 100 * 30))
        #
        #
        # driver.set_window_size(self.width, c)
        # x3 = element.size['height']
        # y4 = driver.get_window_size().get('height')
        #
        # element = driver.find_element(By.XPATH, "//div[@class='thumb-vertical']")
        # xxx = element.value_of_css_property('height')
        # xxx = element.value_of_css_property('height')
        # xxx = element.value_of_css_property('height')
        # xxx = element.value_of_css_property('height')
        #
        # # print width
        # print(element.value_of_css_property('width'))
        #
        #
        #
        #
        #
        #
        # def get_css_properties(element):
        #     properties_dictionary = {}
        #     properties = driver.execute_script('return window.getComputedStyle(arguments[0], null);', element)
        #     for property_ in properties:
        #         properties_dictionary[property_] = element.value_of_css_property(property_)
        #     return properties_dictionary
        #
        # element = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, "body")))
        #
        # css_props = get_css_properties(element)
        # #print(json.dumps(css_props, indent=4, sort_keys=True))
        #
        #
        #
        #
        # scroll = 0
        # while scroll < 3:  # this will scroll 3 times
        #     driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
        #                           element)
        #     scroll += 1
        #     # add appropriate wait here, of course. 1-2 seconds each
        #     time.sleep(2)
        #
        #
        # w, h = size['width'], size['height']
        #
        # driver.execute_script("window.scroll(0,2000)", "")
        #
        #
        #
        # lenOfPage = driver.execute_script(
        #     "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        # match = False
        # while (match == False):
        #     lastCount = lenOfPage
        #     time.sleep(3)
        #     lenOfPage = driver.execute_script(
        #         "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        #     if lastCount == lenOfPage:
        #         match = True
        #
        # xxx = driver.execute_script('return document')
        # xxx = driver.execute_script('return box.left + (arguments[2] || box.width / 2', element)
        # xxx = driver.execute_script('return box.top + (arguments[3] || box.height / 2', element)
        # xxx = driver.execute_script('return arguments', element)
        # xxx = driver.execute_script('return arguments', element)
        # xxx = driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', element)
        # xxx = driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', element)
        # from selenium.webdriver.common.keys import Keys
        # element = driver.find_element(By.TAG_NAME, "body")
        # element.is_enabled()
        # element.click()
        # driver.execute_script("coordinates = arguments[0].getBoundingClientRect();scrollTo(coordinates.x,coordinates.y);", element)
        # scroll_height = element.get_attribute("scrollHeight")
        # scroll_height = element.get_attribute("scrollHeight")
        # scroll_height = element.get_attribute("scrollHeight")
        # #element.is_enabled()
        # #element.click()
        # #element.send_keys(Keys.END)
        #
        #
        # text_length = element.is_displayed()
        # text_length = element.is_displayed()
        # text_length = element.is_displayed()
        # text_length = element.is_displayed()
        # text_length = element.is_displayed()
        #
        #
        #
        # # xxx = driver.execute_script("return document.body.scrollHeight")
        # # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # # yyy = driver.execute_script("return document.body.scrollHeight")
        # driver.set_window_position(0, 0)
        # driver.set_window_size(self.width, last_height)
        #
        # title = driver.title
        # png = driver.get_screenshot_as_png()
        # driver.quit()
        # return dict(img=png, title=title)
