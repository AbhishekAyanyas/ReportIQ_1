from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ReportIQ"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 5500

    class Config:
        env_file = ".env"

settings = Settings()
