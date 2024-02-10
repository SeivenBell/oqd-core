import os

from datetime import datetime, timedelta

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from passlib.context import CryptContext

########################################################################################

from quantumion.server.model import Token, User

from quantumion.server.database import UserInDB, db_dependency

########################################################################################

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

########################################################################################


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
