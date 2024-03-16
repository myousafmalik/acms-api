import traceback
from datetime import date

from fastapi import (
    APIRouter,
    status,
    Depends,
    Response,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from controller import deps
from controller.deps import is_authenticated
from controller.utils import users_dict, generate_random_number
from schema.userSchema import UserLogin, UserSignUp, GetUserProfile, UpdateUserProfile

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
        -password: str
    ```
    and returns an uid
    """
    response = {}
    try:
        outs = session.execute(
            "SELECT * FROM crew_personal where `p-no` = :p_no", {"p_no": user.p_no}
        )
        ress = outs.fetchone()
        if ress is not None:
            res.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the uid already exists",
            )

        data = {"r_id": 77, "password": user.password}
        statement = text(
            """INSERT INTO users(role_id, password) VALUES(:r_id, :password)"""
        )
        session.execute(statement, data)

        # Fetch the last inserted ID using the LAST_INSERT_ID() function
        res = session.execute("SELECT LAST_INSERT_ID() as uid")
        inserted_row = res.fetchone()
        uid = inserted_row.uid

        data = {"uid": uid, "role_id": 77}
        statement = text(
            """INSERT INTO users_roles(user_id, role_id) VALUES(:uid, :role_id)"""
        )
        session.execute(statement, data)

        data = {
            "p_no": user.p_no,
            "email": user.email,
            "_date": date.today(),
        }
        statement = text(
            """INSERT INTO 
            crew_personal(`p-no`, email, name, gender, email2, base, marital_status, seniority, eye_color, hair_color, dob, employment, Image) 
                                  VALUES(:p_no, :email, '', '', '', '', '', '', '', '', :_date, :_date, '')"""
        )
        session.execute(statement, data)

        session.commit()

        response = {
            "status_code": status.HTTP_201_CREATED,
            "detail": "User created successfully",
            "uid": uid,
        }
        return jsonable_encoder(response)
    except Exception as e:
        session.rollback()
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
        -uid: int
        -password: str
        -p_no: str
    ```
    returns a secret key to be used for authentication
    """
    try:
        outs = session.execute(
            "SELECT * FROM users where uid = :uid and password = :password",
            {"uid": user.uid, "password": user.password},
        )
        db_user = outs.fetchone()

        if db_user is None:
            res = {
                "status_code": status.HTTP_403_FORBIDDEN,
                "detail": "Wrong uid or password",
            }
            return res

        outs = session.execute(
            "SELECT * FROM crew_personal where `p-no` = :p_no",
            {"p_no": user.p_no},
        )
        db_user = outs.fetchone()

        if db_user:
            users_dict[user.p_no] = str(generate_random_number(size=7))
            res = {
                "status_code": status.HTTP_201_CREATED,
                "detail": "Login Successfully",
                "secret_key": users_dict[user.p_no],
            }
            return res

        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid p_no",
        )

    except Exception as e:
        print("Error", e)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unexpected Error"
        )


@auth_router.patch("/{cid}/profile", status_code=status.HTTP_201_CREATED)
async def profile(
    cid: str,
    secret: str,
    payload: GetUserProfile,
    session: Session = Depends(deps.get_session),
):
    """
    ## Add profile

    This requires the following
    cid: str (p_no)
    secret: str
    """
    # is_authenticated(cid, secret)
    try:

        sql_query = """
            SELECT *
            FROM crew_personal
            WHERE crew_personal.`p-no` = :p_no limit 1"""

        params = {"p_no": cid}

        # Execute the
        user_profile = session.execute(text(sql_query), params)
        user_profile = user_profile.fetchone()
        if user_profile is None:
            response = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Profile not found",
            }
            return response

        user_profile = UpdateUserProfile(**user_profile)
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
async def get_profile(
    cid: str, secret: str, session: Session = Depends(deps.get_session)
):
    """
    ## Get profile
    This requires the following
    ```
        cid: str (p_no)
        secret: str
    ```
    """
    # is_authenticated(cid, secret)

    response = {}
    try:
        sql_query = """
            SELECT *
            FROM crew_personal
            WHERE crew_personal.`p-no` = :p_no limit 1"""

        params = {"p_no": cid}

        # Execute the query
        user_profile = session.execute(text(sql_query), params)
        user_profile = user_profile.fetchone()
        if user_profile is None:
            response = {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Profile not found",
            }
            return response

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Profile retrieved successfully",
            "profile": GetUserProfile(**user_profile),
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error retrieving profile",
            "error": str(e),
        }

    return response
