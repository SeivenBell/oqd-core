import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String

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


class UserInDB(Base):
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


Base.metadata.create_all(engine)
