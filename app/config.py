from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "Legare123 Mission of Prosperity - De Jure Mission API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legare.db")
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
