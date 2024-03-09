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
from fastapi.responses import FileResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from sqlalchemy import text

from controller import deps

flight_router = APIRouter(prefix="/flight", tags=["flight"])


@flight_router.get("/{cid}/get_flights", status_code=status.HTTP_200_OK)
async def get_flights(
    cid,
    start_date="2021-01-01",
    end_date="2024-12-31",
    session: Session = Depends(deps.get_session),
):
    """
    ## Get all flights
    This requires the following
    ```
        cid: crew id (p_no)
    ```
    """
    response = {}
    try:
        sql_query = """
            SELECT DISTINCT cc_roster.cc_route_no, crew_personal.*, cc_routes.*, cc_route_details.*, flightschedule.*
            FROM crew_personal
            INNER JOIN cc_roster ON crew_personal.`p-no` = cc_roster.p_no
            INNER JOIN cc_routes ON cc_roster.cc_route_no = cc_routes.cc_route_no
            INNER JOIN cc_route_details ON cc_routes.cc_route_no = cc_route_details.cc_route_no
            INNER JOIN flightschedule ON cc_route_details.flight_no = flightschedule.FlightNo
            WHERE crew_personal.`p-no` = :p_no 
            AND cc_route_details.f_dep_date BETWEEN :f_dep_date1 AND :f_dep_date2
        """

        # Execute the query
        flights = session.execute(
            text(sql_query),
            {"p_no": cid, "f_dep_date1": start_date, "f_dep_date2": end_date},
        )

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Flights retrieved successfully",
            "flights": [flight for flight in flights],
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error retrieving flights",
            "error": str(e),
        }
    return response


@flight_router.get("/{cid}/get_flights/{fid}", status_code=status.HTTP_200_OK)
async def get_flights(cid, fid: int, session: Session = Depends(deps.get_session)):
    """
    ## Get all flights
    This requires the following
    ```
        -flight id
    ```
    """
    try:
        sql_query = """
            SELECT DISTINCT cc_roster.cc_route_no, crew_personal.*, cc_routes.*, cc_route_details.*, flightschedule.*
            FROM crew_personal
            INNER JOIN cc_roster ON crew_personal.`p-no` = cc_roster.p_no
            INNER JOIN cc_routes ON cc_roster.cc_route_no = cc_routes.cc_route_no
            INNER JOIN cc_route_details ON cc_routes.cc_route_no = cc_route_details.cc_route_no
            INNER JOIN flightschedule ON cc_route_details.flight_no = flightschedule.FlightNo
            WHERE flightschedule.FlightNo = :fid and crew_personal.`p-no` = :p_no
        """
        # Execute the query
        flights = session.execute(text(sql_query), {"fid": fid, "p_no": cid})

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Flights retrieved successfully",
            "flights": [flight for flight in flights],
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error retrieving flights",
            "error": str(e),
        }
    return response
