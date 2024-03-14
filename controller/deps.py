from typing import Generator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from controller.database import Session
from controller.utils import users_dict


def get_session() -> Generator:
    db = Session()
    try:
        yield db
    finally:
        db.close()


def is_authenticated(p_no: str, secret: str):
    if p_no not in users_dict or users_dict[p_no] != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authenticated",
        )
