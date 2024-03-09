from typing import List, Generator
from functools import wraps
import json
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from controller.database import Session


def get_session() -> Generator:
    db = Session()
    try:
        yield db
    finally:
        db.close()
