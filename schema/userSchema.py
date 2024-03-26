from pydantic import BaseModel
from typing import Any


class UserLogin(BaseModel):
    p_no: str
    password: str
    uid: int | None = None


class UserSignUp(BaseModel):
    p_no: str
    email: str
    password: str


class UpdateUserProfile(BaseModel):
    name: str | None = None
    alias: str | None = None
    dob: Any | None = None
    gender: str | None = None
    email: str | None = None
    email2: str | None = None
    number: str | None = None
    number2: str | None = None
    base: str | None = None
    marital_status: str | None = None
    employment: Any | None = None
    seniority: str | None = None
    height: float | None = None
    weight: float | None = None
    eye_color: str | None = None
    hair_color: str | None = None


class GetUserProfile(UpdateUserProfile, BaseModel):
    p_no: str | None = None
    image: Any | None = None
