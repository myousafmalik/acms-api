import os
import traceback
from datetime import datetime, date
from uuid import uuid4

from fastapi import (
    APIRouter,
    status,
    Depends,
    Request,
    Response,
    File,
    UploadFile,
    Form,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT

from sqlalchemy.orm import Session

from controller import deps
from schema.userSchema import UserLogin, UserSignUp
from sqlalchemy import text

auth_router = APIRouter(prefix="/user", tags=["user"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserSignUp,
    res: Response,
    session: Session = Depends(deps.get_session),
    Authorize: AuthJWT = Depends(),
):
    """
    ## Create a user
    This requires the following
    ```
        -p_no: int
        -email: str
    ```

    """
    response = {}
    try:
        outs = session.execute(
            "SELECT * FROM crew_personal where p-no = :p-no", {"p-no": user.p_no}
        )
        ress = outs.fetchone()
        if ress is not None:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the uid already exists",
            )

        data = {"uid": user.p_no, "role_id": 77, "password": user.password}
        statement = text(
            """INSERT INTO usesrs(p_no, role_id, password) VALUES(:uid, :role_id, :password)"""
        )
        session.execute(statement, **data)

        data = {"user_id": user.p_no, "role_id": 77}
        statement = text(
            """INSERT INTO users_roles(uid, role_id) VALUES(:uid, :role_id)"""
        )
        session.execute(statement, **data)

        session.commit()

        response = {
            "status_code": status.HTTP_201_CREATED,
            "detail": "User created successfully",
            "p_no": user.p_no,
        }
        return jsonable_encoder(response)
    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error"
        )


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(
    user: UserLogin,
    req: Request,
    response: Response,
    session: Session = Depends(deps.get_session),
    Authorize: AuthJWT = Depends(),
):
    """
    ## Login a user
    This requires
        ```
            p_no:int
            email:str
        ```
    and returns a token pair `access`
    """
    try:
        outs = session.execute(
            "SELECT * FROM crew_personal where p-no = :p-no and email = :email",
            {"p-no": user.p_no, "email": user.emailF},
        )
        db_user = outs.fetchone()

        if db_user:
            res = {
                "status_code": status.HTTP_201_CREATED,
                "detail": "Login Successfully",
                "p_no": db_user.p_no,
            }
            return res

        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid p_no Or email",
        )

    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error"
        )
