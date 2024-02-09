from pydantic import BaseModel

########################################################################################


class UserRegistrationForm(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    userid: int
    username: str
