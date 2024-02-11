import os

from typing import Annotated

from redis import Redis
from rq import Queue

from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import asyncio

from contextlib import asynccontextmanager

########################################################################################

REDIS_HOST = os.environ["REDIS_HOST"]

redis_client = Redis(host=REDIS_HOST, port=6379, decode_responses=False)
queue = Queue(connection=redis_client)

########################################################################################

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_async_engine(POSTGRES_URL)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

########################################################################################


class Base(DeclarativeBase):
    pass


class UserInDB(Base):
    __tablename__ = "users"

    userid: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)


class JobInDB(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    task: Mapped[str] = mapped_column(nullable=False)
    backend: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    result: Mapped[str] = mapped_column(nullable=True)
    userid: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)


########################################################################################


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


db_dependency = Annotated[AsyncSession, Depends(get_db)]

########################################################################################


async def _report_success(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="finished", result=result.model_dump_json())
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_success(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_success(job, connection, result, *args, **kwargs)
    )


async def _report_failure(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="failed")
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_failure(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_failure(job, connection, result, *args, **kwargs)
    )


async def _report_stopped(job, connection, result, *args, **kwargs):
    async with asynccontextmanager(get_db)() as db:
        status_update = dict(status="stopped")
        query = await db.execute(select(JobInDB).filter(JobInDB.job_id == job.id))
        job_in_db = query.scalars().first()
        for k, v in status_update.items():
            setattr(job_in_db, k, v)
        await db.commit()


def report_stopped(job, connection, result, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        _report_stopped(job, connection, result, *args, **kwargs)
    )
