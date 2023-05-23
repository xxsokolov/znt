from configparser import ConfigParser
config = ConfigParser()
config.read("znt.cfg", encoding='utf-8')

from app.classes import logger
logger = logger.Log(debug=True if config.get('logging', 'logging_level') == 'DEBUG' else False)
# bool(True if config.get('logging', 'logging_level') == 'DEBUG' else False)