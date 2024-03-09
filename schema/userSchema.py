from pydantic import BaseModel
from typing import Union


class UserLogin(BaseModel):
    p_no:int
    email: str


class UserSignUp(BaseModel):
    p_no:int
    email: str