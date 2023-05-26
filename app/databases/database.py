# -*- coding: utf-8 -*-
########################
#    Sokolov Dmitry    #
# xx.sokolov@gmail.com #
#  https://t.me/ZbxNTg #
########################
# https://github.com/xxsokolov/znt
from sqlalchemy import create_engine  #, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.engine import URL
# from sqlalchemy import inspect
# import os
from app import config


# config = configparser.ConfigParser()
# config.read("znt.cfg")

# xxx = config.get('core', 'sqlalchemy_conn')
# url_object = URL.create(
#     "postgresql+psycopg2",
#     username=os.environ.get("ZNT_DB_USER"),
#     password=os.environ.get("ZNT_DB_PWD"),
#     host=os.environ.get("ZNT_DB_HOST"),
#     port=os.environ.get("ZNT_DB_PORT"),
#     database=os.environ.get("ZNT_DB_BASE")
# )
# db_schema = os.environ.get("ZNT_DB_SCHEMA")
# meta = MetaData(schema=db_schema)
# debug_mode = bool(True if config.get('logging', 'logging_level') == 'DEBUG' else False)
engine = create_engine(config.get('core', 'sqlalchemy_conn'), connect_args={"application_name": "ZNT"},
                       pool_size=2, max_overflow=8, pool_recycle=300, pool_pre_ping=True, pool_use_lifo=True)

# inspector = inspect(engine)
# all_schemas = inspector.get_schema_names()
# for schema in [meta.schema]:
#     if schema not in all_schemas:
#         with engine.connect() as connection:
#             result = connection.execute(text("CREATE SCHEMA {}".format(schema)))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()



