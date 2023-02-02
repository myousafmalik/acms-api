from pydantic import BaseModel
from typing import Union


class UserLogin(BaseModel):
    email: str
    password: str


class UserSignUp(BaseModel):
    name: str
    email: str
    password: str | None = None


class UserForget(BaseModel):
    email: str
    new_password: str

