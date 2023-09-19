from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str

    SECRET_KEY: str
    EXPIRE_MINUTES: int
    ALGORITHM: str

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CONTEXT_KEY: str

    CELERY_RESULT_BACKEND: str
    CELERY_BROKER_URL: str

    class Config:
        env_file = "../.env"


def get_settings() -> Settings:
    return Settings()
