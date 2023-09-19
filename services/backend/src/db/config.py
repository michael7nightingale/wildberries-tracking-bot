from piccolo.engine import PostgresEngine

from settings import get_settings


settings = get_settings()


DB = PostgresEngine(
    config={
        "database": settings.DB_NAME,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD
    }
)
