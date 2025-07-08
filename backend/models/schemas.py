from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


class Tokens(BaseModel):
    access: str
    refresh: str
