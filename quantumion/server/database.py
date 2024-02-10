import os

from redis import Redis
from rq import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String

########################################################################################

REDIS_HOST = os.environ["REDIS_HOST"]

redis_client = Redis(host=REDIS_HOST, port=6379, decode_responses=False)
queue = Queue(connection=redis_client)

########################################################################################

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

########################################################################################


class UserInDB(Base):
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class JobInDB(Base):
    __tablename__ = "jobs"

    jobid = Column(String, primary_key=True, index=True)
    userid = Column(Integer, nullable=False)
    username = Column(String, nullable=False)


Base.metadata.create_all(engine)
