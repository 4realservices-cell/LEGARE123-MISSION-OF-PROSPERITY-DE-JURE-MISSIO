import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "LEGARE123 Mission of Prosperity")
    app_env: str = os.getenv("APP_ENV", "development")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    api_prefix: str = os.getenv("API_PREFIX", "/api")


settings = Settings()
