# -*- coding: utf-8 -*-
####################################
#          Sokolov Dmitry          #
#       xx.sokolov@gmail.com       #
#        https://t.me/ZbxNTg       #
####################################
# https://github.com/xxsokolov/znt #
####################################
import sys
import logging
import os
from app import config


class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    green = '\x1b[32m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[31m'
    bold_red = '\x1b[38;5;196m'
    reset = '\x1b[0m'
    # format =

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.green + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Log:
    def __init__(self, debug=False):
        if debug:
            self.log_level = logging.DEBUG
        else:
            self.log_level = logging.INFO

        global_format = "[%(asctime)s] - PID:%(process)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s"
        self.log = logging.getLogger(None if debug else __name__)
        self.log.setLevel(self.log_level)
        logging.getLogger('sqlalchemy.engine').setLevel(self.log_level)
        logging.getLogger('sqlalchemy.pool').setLevel(self.log_level)

        self.uvicorn_logger = logging.getLogger('uvicorn')
        self.uvicorn_logger.propagate = False

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(self.log_level)
        stdout_handler.setFormatter(CustomFormatter(fmt=global_format))

        current = os.path.dirname(os.path.realpath(__file__))
        parent = os.path.dirname(current)
        log_file = config.get('logging', 'log_file')

        if not log_file:
            os.makedirs(os.path.join(parent, 'logs'), exist_ok=True)
        file_handler = logging.FileHandler(filename=log_file if log_file else os.path.join(parent, 'logs', 'znt.log'),
                                           mode='a')
        file_handler.setLevel(self.log_level)
        file_handler_format = logging.Formatter(global_format)
        file_handler.setFormatter(fmt=file_handler_format)

        self.log.addHandler(stdout_handler)
        self.uvicorn_logger.addHandler(stdout_handler)

        self.log.addHandler(file_handler)
        self.uvicorn_logger.addHandler(file_handler)

    def close_file_handler(self):
        for handler in self.log.root.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)

    def get_level_name(self):
        return logging.getLevelName(self.log.getEffectiveLevel())
