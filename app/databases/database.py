from sqlalchemy import create_engine, MetaData, schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgrespw@localhost:32770/fastapi"

tg_schema = "telegram"
meta = MetaData(schema=tg_schema)
engine = create_engine(SQLALCHEMY_DATABASE_URL, encoding='UTF8', echo=True)

inspector = inspect(engine)
all_schemas = inspector.get_schema_names()
for schema in [meta.schema]:
    if schema not in all_schemas:
        engine.execute(f"CREATE SCHEMA {schema}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=meta)


