from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    TOKEN: str
    TELEGRAM_CONTEXT_KEY: str
    API_BASE_URL: str
    SECRET_KEY: str
    EXPIRE_MINUTES: int
    ALGORITHM: str

    class Config:
        if os.getenv("DOCKER"):
            env_file = "../docker.env"
        else:
            env_file = "../dev.env"


def get_settings() -> Settings:
    return Settings()
