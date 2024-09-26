from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from . import models
import os
from dotenv import load_dotenv

load_dotenv()

file_path = os.path.dirname(__file__)
string = "sqlite:///"
database_header = "sqlite:///" if os.name == "nt" else "sqlite:////"

SQLALCHEMY_DATABASE_URL = f"{database_header}{file_path}/triage.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=MetaData())

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()