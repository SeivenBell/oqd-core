import os

from typing import Annotated

from redis import Redis
from rq import Queue

from fastapi import Depends

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

########################################################################################


class UserInDB(Base):
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class JobInDB(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)
    task = Column(String, nullable=False)
    backend = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(String, nullable=True)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    username = Column(String, ForeignKey("users.username"), nullable=False)


Base.metadata.create_all(engine)

########################################################################################


def report_success(job, connection, result, *args, **kwargs):
    db = next(get_db())
    status_update = dict(status="finished", result=result.model_dump_json())
    db.query(JobInDB).filter(JobInDB.job_id == job.id).update(status_update)
    db.commit()


def report_failure(job, connection, result, *args, **kwargs):
    db = next(get_db())
    status_update = dict(status="failed")
    db.query(JobInDB).filter(JobInDB.job_id == job.id).update(status_update)
    db.commit()


def report_stopped(job, connection, result, *args, **kwargs):
    db = next(get_db())
    status_update = dict(status="stopped")
    db.query(JobInDB).filter(JobInDB.job_id == job.id).update(status_update)
    db.commit()
