from fastapi import (
    APIRouter,
    status,
    Depends,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from controller import deps
from controller.deps import is_authenticated

flight_router = APIRouter(prefix="/flight", tags=["flight"])


# Get all flights
@flight_router.get("/get_flights", status_code=status.HTTP_200_OK)
async def get_flights(
    cid: str,
    secret: str,
    start_date="2021-01-01",
    end_date="2024-12-31",
    session: Session = Depends(deps.get_session),
):
    """
    ## Get all flights of all crews

    This requires the following
    ```
        cid: crew id (p_no)
        secret: str
        start_date: start date (OPTIONAL)
        end_date: end date (OPTIONAL)
    ```
    """
    # is_authenticated(cid, secret)

    response = {}
    try:
        sql_query = """
                SELECT DISTINCT cc_route_details.f_dep_date, cc_route_details.f_dep_station, flightschedule.DepPort, flightschedule.ArrPort, flightschedule.DepTime, flightschedule.ArrTime, flightschedule.FlightNo, flightschedule.ACType
                FROM crew_personal
                INNER JOIN cc_roster ON crew_personal.`p-no` = cc_roster.p_no
                INNER JOIN cc_routes ON cc_roster.cc_route_no = cc_routes.cc_route_no
                INNER JOIN cc_route_details ON cc_routes.cc_route_no = cc_route_details.cc_route_no
                INNER JOIN flightschedule ON cc_route_details.flight_no = flightschedule.FlightNo
                """

        params = {}

        if start_date and end_date:
            sql_query += """ WHERE cc_route_details.f_dep_date BETWEEN :f_dep_date1 AND :f_dep_date2"""
            params["f_dep_date1"] = start_date
            params["f_dep_date2"] = end_date

        # Execute the query
        flights = session.execute(text(sql_query), params)

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


@flight_router.get("/{cid}/get_flights", status_code=status.HTTP_200_OK)
async def get_flights(
    cid: str,
    secret: str,
    start_date="2021-01-01",
    end_date="2024-12-31",
    session: Session = Depends(deps.get_session),
):
    """
    ## Get all flights
    This requires the following
    ```
        cid: crew id (p_no)
        secret: str
        start_date: start date (OPTIONAL)
        end_date: end date (OPTIONAL)
    ```
    """
    # is_authenticated(cid, secret)
    response = {}
    try:
        sql_query = """
            SELECT DISTINCT cc_route_details.f_dep_date, cc_route_details.f_dep_station, flightschedule.DepPort, flightschedule.ArrPort, flightschedule.DepTime, flightschedule.ArrTime, flightschedule.FlightNo, flightschedule.ACType
            FROM crew_personal
            INNER JOIN cc_roster ON crew_personal.`p-no` = cc_roster.p_no
            INNER JOIN cc_routes ON cc_roster.cc_route_no = cc_routes.cc_route_no
            INNER JOIN cc_route_details ON cc_routes.cc_route_no = cc_route_details.cc_route_no
            INNER JOIN flightschedule ON cc_route_details.flight_no = flightschedule.FlightNo
            WHERE crew_personal.`p-no` = :p_no"""

        params = {"p_no": cid}

        if start_date and end_date:
            sql_query += """ AND cc_route_details.f_dep_date BETWEEN :f_dep_date1 AND :f_dep_date2"""
            params["f_dep_date1"] = start_date
            params["f_dep_date2"] = end_date

        # Execute the query
        flights = session.execute(text(sql_query), params)

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
async def get_flights(
    cid: str, fid: int, secret: str, session: Session = Depends(deps.get_session)
):
    """
    ## Get all flights
    This requires the following
    ```
        -cid: crew id (p_no)
        -flight id
        -secret: str
    ```
    """
    try:
        # is_authenticated(cid, secret)

        sql_query = """
            SELECT DISTINCT cc_roster.cc_route_no, crew_personal.*, cc_routes.*, cc_route_details.*, flightschedule.*
            FROM crew_personal
            INNER JOIN cc_roster ON crew_personal.`p-no` = cc_roster.p_no
            INNER JOIN cc_routes ON cc_roster.cc_route_no = cc_routes.cc_route_no
            INNER JOIN cc_route_details ON cc_routes.cc_route_no = cc_route_details.cc_route_no
            INNER JOIN flightschedule ON cc_route_details.flight_no = flightschedule.FlightNo
            WHERE flightschedule.FlightNo = :fid and crew_personal.`p-no` = :p_no limit 1
        """
        # Execute the query
        flights = session.execute(text(sql_query), {"fid": fid, "p_no": cid})

        response = {
            "status_code": status.HTTP_200_OK,
            "detail": "Flights retrieved successfully",
            "flight": [flight for flight in flights][0],
        }
    except Exception as e:
        response = {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Error retrieving flights",
            "error": str(e),
        }
    return response
