import os

from datetime import datetime, timedelta, timezone

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

########################################################################################

from quantumion.server.database import SessionLocal

from quantumion.server.model import UserRegistrationForm

from quantumion.server.database import User

########################################################################################

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, create_user_form: UserRegistrationForm):

    user = User(
        username=create_user_form.username,
        hashed_password=pwd_context.hash(create_user_form.password),
    )

    db.add(user)
    db.commit()
    pass
