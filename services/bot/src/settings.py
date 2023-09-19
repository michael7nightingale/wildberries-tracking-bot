from pydantic import BaseSettings


class Settings(BaseSettings):
    TOKEN: str
    TELEGRAM_CONTEXT_KEY: str
    API_BASE_URL: str
    SECRET_KEY: str
    EXPIRE_MINUTES: int
    ALGORITHM: str

    class Config:
        env_file = "../.env"


def get_settings() -> Settings:
    return Settings()
