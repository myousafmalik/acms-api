import os

from pathlib import Path


class Settings:
    PROJECT_NAME: str = "ACMS"
    PROJECT_VERSION: str = "1.0.0"

    DB_NAME: str = "fyp"
    DATABASE_URL = f"mysql+pymysql://root:12345678@localhost:3306/{DB_NAME}"


settings = Settings()
