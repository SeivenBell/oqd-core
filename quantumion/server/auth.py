import os

from datetime import datetime, timedelta

from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

########################################################################################

from quantumion.server.database import SessionLocal

from quantumion.server.model import UserRegistrationForm, Token, User

from quantumion.server.database import UserInDB

########################################################################################

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

########################################################################################


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

########################################################################################


def available_user(user, db):
    user_in_db = db.query(UserInDB).filter(UserInDB.username == user.username).first()
    if not user_in_db:
        return user

    raise HTTPException(status_code=status.HTTP_409_CONFLICT)


def authenticate_user(user, db):
    user_in_db = db.query(UserInDB).filter(UserInDB.username == user.username).first()
    if user_in_db and pwd_context.verify(user.password, user_in_db.hashed_password):
        return user_in_db

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def generate_token(username, userid):
    expires = datetime.utcnow() + timedelta(
        minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    encode = {"id": userid, "sub": username, "exp": expires}
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        userid = payload.get("id")
        if not username is None and not userid is None:
            return User(username=username, userid=userid)
        raise JWTError

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


user_dependency = Annotated[User, Depends(current_user)]

# ########################################################################################


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(create_user_form: UserRegistrationForm, db: db_dependency):
    user = available_user(create_user_form, db)
    if user:
        user_in_db = UserInDB(
            username=user.username,
            hashed_password=pwd_context.hash(user.password),
        )

        db.add(user_in_db)
        db.commit()
    pass


@router.post("/token")
async def request_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user_in_db = (
        db.query(UserInDB).filter(UserInDB.username == form_data.username).first()
    )
    if user_in_db and pwd_context.verify(
        form_data.password, user_in_db.hashed_password
    ):
        token = generate_token(user_in_db.username, user_in_db.userid)
        return Token(access_token=token, token_type="bearer")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
