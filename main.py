import os

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

from config import settings
from controller.database import Base, engine
from routes.user_route import auth_router


def create_tables():  # new
    Base.metadata.create_all(bind=engine)


def include_router(app_instance):
    app_instance.include_router(auth_router)


def start_application():
    app_instance = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app_instance)
    create_tables()  # new
    return app_instance


app = start_application()


class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("SECRET_KEY")


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="TB Data Collection",
        version="0.0.1",
        description="Tb Data Collection APIS, to store audios",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get routes from index 4 because before that fastapi define router for /openapi.json, /redoc, /docs, etc
    # Get all router where operation_id is authorize
    router_authorize = [route for route in app.routes[4:] if route.operation_id == "authorize"]
    for route in router_authorize:
        method = list(route.methods)[0].lower()
        path = getattr(route, "path")
        openapi_schema["paths"][path][method]["security"] = [
            {
                "Bearer Auth": []
            }
        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# app.include_router(recipe_router)
# app.include_router(food_router)
# app.include_router(all_food_router)
# app.include_router(misc_router)
