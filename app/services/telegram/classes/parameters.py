# -*- coding: utf-8 -*-
####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import yaml
import json
from types import SimpleNamespace
from app import logger


class ReadParam:

    def __init__(self, path=None, json=None):
        self.path = path
        self.json = json
        self.namespace = None
        self.dict = None
        self.logger = logger.log
        #self.args = args

    def read_command_line(self):
        self.logger.debug('Получаем параметры запуска')
        yyy = self.args.parameters.replace("\\r\\n", "\n")
        data = yaml.load(stream=yyy, Loader=yaml.FullLoader)
        #self.namespace = json.loads(json.dumps(data), object_hook=lambda item: SimpleNamespace(**item))
        return data

    def read_api_mode(self) -> SimpleNamespace:
        self.logger.debug('Получаем параметры запуска')
        if len(self.json) < 1:
            raise Exception("Список ботов пустой. Добавьте ботов в базу")
        self.namespace = json.loads(json.dumps(self.json, default=str), object_hook=lambda item: SimpleNamespace(**item))
        return self.namespace

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
