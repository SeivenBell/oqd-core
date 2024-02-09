from pydantic import BaseModel

########################################################################################


class UserRegistrationForm(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
