from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Legare123 Mission of Prosperity - De Jure Mission API"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
