from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "Legare123 Mission of Prosperity - De Jure Mission API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legare.db")
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/legare")
    api_prefix: str = "/api/v1"
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    class Config:
        env_file = ".env"

settings = Settings()
