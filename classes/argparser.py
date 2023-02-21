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
import textwrap
from argparse import RawTextHelpFormatter


class ArgParsing:

    def __init__(self):
        self.argparse = argparse
        self.parser = None
        #self.parent_group = None
        self.subparsers = None
        #self.file_mode_parser = None
        #self.discovery_mode_parser = None
        self.zabbix = None
        self.api = None
        self.console = None
        self.init = None

    def create_parser(self):
        self.parser = self.argparse.ArgumentParser(
            prog='znt',
            description='''Скрипт для для отправки Zabbix нотификаций в Telegram''',
            epilog='''2.0 (c) Dmitry Sokolov 2023 @ https://github.com/xxsokolov/''',
            add_help=False, formatter_class=RawTextHelpFormatter)

        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers(dest='command', title='Режимы')

        self.zabbix = self.subparsers.add_parser('zabbix')
        self.zabbix.add_argument('username', nargs='?', help='Set username Telegram')
        # self.zabbix.add_argument('--MainConfigYaml',default='.main_config.yaml', required=False, type=str)
        self.zabbix.add_argument('--debug', type=str, nargs='?', const=True, default=False, help='Debug mode')

        self.api = self.subparsers.add_parser('api')
        self.api.add_argument('username', nargs='?', help='Set username Telegram')
        # self.zabbix.add_argument('--MainConfigYaml',default='.main_config.yaml', required=False, type=str)
        self.api.add_argument('--debug', type=str, nargs='?', const=True, default=False, help='Debug mode')

        self.console = self.subparsers.add_parser('console')
        #self.console.add_argument('--MainConfigYaml',default='.main_config.yaml', required=False, type=str)
        self.console.add_argument('--Username', nargs='?', required=True, help='Set username Telegram')
        self.console.add_argument('--SendConfigYaml', default='.send_config.yaml', required=False, type=str)
        self.console.add_argument('--BotConfigYaml', default='.bots.yaml', required=False, type=str)
        self.console.add_argument('--debug', type=str, nargs='?', const=True, default=False, help='Debug mode')

        self.init = self.subparsers.add_parser('init')

        return self.parser
