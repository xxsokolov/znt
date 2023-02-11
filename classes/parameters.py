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

import yaml
import json
from types import SimpleNamespace


class ReadYaml:

    def __init__(self, logger, path):
        self.path = path
        self.namespace = None
        self.dict = None
        self.logger = logger
        #self.args = args

    def read_command_line(self):
        self.logger.debug('Получаем параметры запуска')
        yyy = self.args.parameters.replace("\\r\\n", "\n")
        data = yaml.load(stream=yyy, Loader=yaml.FullLoader)
        #self.namespace = json.loads(json.dumps(data), object_hook=lambda item: SimpleNamespace(**item))
        return data

    def read_yaml(self) -> SimpleNamespace:
        self.logger.debug('Чтение yaml файла {}'.format(self.path))
        try:
            with open(self.path) as f:
                data = yaml.load(stream=f, Loader=yaml.FullLoader)
            # Формируем рекурсивный namespace
            self.namespace = json.loads(json.dumps(data), object_hook=lambda item: SimpleNamespace(**item))
        except Exception as err:
            self.logger.critical('Чтение yaml файла завершилось ошибкой. ({}) Error: {} '.format(self.path, err))
            raise SystemExit(1)
        else:
            self.logger.debug('Чтение yaml файла выполнено успешно.')
            return self.namespace

    def read_bots_yaml(self) -> dict:
        self.logger.debug('Чтение yaml файла {}'.format(self.path))
        try:
            with open(self.path) as f:
                self.dict = yaml.load(stream=f, Loader=yaml.FullLoader)
            # Формируем рекурсивный namespace
            # self.namespace = json.loads(json.dumps(data), object_hook=lambda item: SimpleNamespace(**item))
        except Exception as err:
            self.logger.critical('Чтение yaml файла завершилось ошибкой. ({}) Error: {} '.format(self.path, err))
            raise SystemExit(1)
        else:
            self.logger.debug('Чтение yaml файла выполнено успешно.')
            return self.dict
