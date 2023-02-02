import os
import traceback
from datetime import datetime, date
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, status, Depends, Request, Response, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from fastapi_jwt_auth import AuthJWT
# from google.auth.transport import requests
# from google.oauth2 import id_token
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from controller import deps
from models.user import User
from schema.userSchema import UserLogin, UserSignUp, GoogleInfo, UserForget

auth_router = APIRouter(
    prefix='/user',
    tags=['user']

)


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignUp, res: Response, session: Session = Depends(deps.get_session),
                 Authorize: AuthJWT = Depends()):
    """
        ## Create a user
        This requires the following
        ```
            -email: str
            -password: str
        ```

    """
    response = {}
    try:
        db_email = session.query(User).filter(User.email == user.email).first()
        if db_email is not None and user.id_token:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="User with the email already exists")

        u_id = str(uuid4())
        new_user = User(
            user_id=u_id,
            email=user.email,
            password=generate_password_hash(user.password) if user.password else None,
            is_active=True,
        )

        session.add(new_user)
        session.commit()
        access_token = Authorize.create_access_token(subject=new_user.user_id, expires_time=False)
        response = {
            'status_code': status.HTTP_201_CREATED,
            'detail': 'User created successfully',
            'email': new_user.email,
        }
        return jsonable_encoder(response)
    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error")


@auth_router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(user: UserLogin, req: Request, response: Response, session: Session = Depends(deps.get_session),
                Authorize: AuthJWT = Depends()):
    """
        ## Login a user
        This requires
            ```
                username:str
                password:str
            ```
        and returns a token pair `access`
    """
    try:
        db_user = session.query(User).filter(User.email == user.email).first()
        if db_user and check_password_hash(db_user.password, user.password):
            access_token = Authorize.create_access_token(subject=db_user.user_id, expires_time=False)
            res = {
                'status_code': status.HTTP_201_CREATED,
                'detail': 'Login Successfully',
                'email': db_user.email,
                'token': access_token,
            }
            return res
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Invalid Username Or Password")
    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error")


@auth_router.post("/forget", status_code=status.HTTP_201_CREATED)
async def forget(info: UserForget, response: Response, session: Session = Depends(deps.get_session)):
    try:
        user = session.query(User).filter(User.email == info.email).first()
        if user:
            user.password = generate_password_hash(info.new_password)
            session.commit()
            return {
                'status_code': status.HTTP_201_CREATED,
                'detail': 'Password updated successfully'
            }

        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User Not found with this email")
    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error")

