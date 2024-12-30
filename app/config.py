from pydantic import BaseSettings

class Settings(BaseSettings):
    google_credentials_file: str
    api_title: str = "Google Meet Management API"
    api_version: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
