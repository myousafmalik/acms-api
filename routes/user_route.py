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
from schema.userSchema import UserLogin, UserSignUp, GetUserProfile, UpdateUserProfile
from sqlalchemy import text

auth_router = APIRouter(prefix="/user", tags=["user"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserSignUp, res: Response, session: Session = Depends(deps.get_session)
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
    user: UserLogin, response: Response, session: Session = Depends(deps.get_session)
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


@auth_router.patch("/{cid}/profile", status_code=status.HTTP_201_CREATED)
async def profile(
    cid: str, payload: GetUserProfile, session: Session = Depends(deps.get_session)
):
    """
    ## Add profile

    This requires the following
    cid: str (p_no)
    """
    try:

        sql_query = """
            SELECT *
            FROM crew_personal
            WHERE crew_personal.`p-no` = :p_no limit 1"""

        params = {"p_no": cid}

        # Execute the
        user_profile = session.execute(text(sql_query), params)
        user_profile = [_profile for _profile in user_profile]
        if len(user_profile) == 0:
            response = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Profile not found",
            }
            return response

        user_profile = UpdateUserProfile(**user_profile[0])
        p_query = ""

        for u_field in user_profile.dict().keys():
            to_update = getattr(payload, u_field)
            if to_update is not None:
                setattr(user_profile, u_field, to_update)

            p_query += f"{u_field} = :{u_field}, "

        p_query = p_query[:-2]
        query = "Update crew_personal SET "
        query += p_query
        query += f" WHERE crew_personal.`p-no` = :p_no"

        session.execute(text(query), {**user_profile.dict(), **{"p_no": cid}})
        session.commit()

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Profile updated successfully",
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error updated",
            "error": str(e),
        }

    return response


@auth_router.get("/{cid}/profile", status_code=status.HTTP_200_OK)
async def get_profile(cid: str, session: Session = Depends(deps.get_session)):
    """
    ## Get profile
    This requires the following
    ```
        cid: str (p_no)
    ```
    """
    response = {}
    try:
        sql_query = """
            SELECT *
            FROM crew_personal
            WHERE crew_personal.`p-no` = :p_no limit 1"""

        params = {"p_no": cid}

        # Execute the query
        user_profile = session.execute(text(sql_query), params)
        user_profile = [_profile for _profile in user_profile]
        if len(user_profile) == 0:
            response = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Profile not found",
            }
            return response

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Profile retrieved successfully",
            "profile": GetUserProfile(**user_profile[0]),
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error retrieving profile",
            "error": str(e),
        }

    return response
