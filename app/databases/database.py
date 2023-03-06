from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy import inspect
from app import models
import os

url_object = URL.create(
    "postgresql+psycopg2",
    username=os.environ.get("ZNT_DB_USER"),
    password=os.environ.get("ZNT_DB_PWD"),
    host=os.environ.get("ZNT_DB_HOST"),
    port=os.environ.get("ZNT_DB_PORT"),
    database=os.environ.get("ZNT_DB_BASE")
)
db_schema = os.environ.get("ZNT_DB_SCHEMA")
meta = MetaData(schema=db_schema)
debug_mode = bool(True if os.environ.get("DEBUG") == 'True' else False)
engine = create_engine(url_object, echo=debug_mode, connect_args={"application_name": "ZNT"})

inspector = inspect(engine)
all_schemas = inspector.get_schema_names()
for schema in [meta.schema]:
    if schema not in all_schemas:
        with engine.connect() as connection:
            result = connection.execute(text("CREATE SCHEMA {}".format(schema)))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=meta)



