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
import uvicorn


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

        self.log = logging.getLogger(None if debug else __name__)
        self.log.setLevel(self.log_level)

        self.uvicorn_logger = logging.getLogger('uvicorn')
        self.uvicorn_logger.propagate = True

        # self.uvicorn_logger_access = logging.getLogger('uvicorn.access')
        # self.uvicorn_logger_access.propagate = True
        #
        # self.uvicorn_logger_error = logging.getLogger('uvicorn.error')
        # self.uvicorn_logger_error.propagate = True

        self.sqlalchemy_engine = logging.getLogger('sqlalchemy.engine').setLevel(self.log_level)
        self.sqlalchemy_pool = logging.getLogger('sqlalchemy.pool').setLevel(self.log_level)
        # self.sqlalchemy_engine.propagate = True

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(self.log_level)
        stdout_handler.setFormatter(CustomFormatter(fmt="[%(asctime)s] - PID:%(process)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s"))

        # file_handler = logging.FileHandler(filename=config_log_file, mode='a')
        # file_handler.setLevel(self.log_level)
        # file_handler.setFormatter(log_format)

        self.log.addHandler(stdout_handler)
        self.uvicorn_logger.addHandler(stdout_handler)
        # self.uvicorn_logger_access.addHandler(stdout_handler)
        # self.uvicorn_logger_error.addHandler(stdout_handler)

        # self.sqlalchemy_engine.setLevel(logging.DEBUG)
        # self.sqlalchemy_engine.addHandler(stdout_handler)
        # self.sqlalchemy_pool.addHandler(stdout_handler)
        # self.log.addHandler(file_handler)

    def close_file_handler(self):
        for handler in self.log.root.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)

    def get_level_name(self):
        return logging.getLevelName(self.log.getEffectiveLevel())
