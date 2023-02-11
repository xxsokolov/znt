# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
import sys
from config import *
import logging


class Log:
    def __init__(self, debug=False):
        if debug:
            self.log_level = logging.DEBUG
        else:
            self.log_level = logging.INFO
        log_format = logging.Formatter(
            '[%(asctime)s] - PID:%(process)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s'
        )
        self.log = logging.getLogger(None if debug else __name__)
        self.log.setLevel(self.log_level)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(self.log_level)
        stdout_handler.setFormatter(log_format)

        file_handler = logging.FileHandler(filename=config_log_file, mode='a')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(log_format)

        self.log.addHandler(stdout_handler)
        self.log.addHandler(file_handler)

    def close_file_handler(self):
        for handler in self.log.root.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)
