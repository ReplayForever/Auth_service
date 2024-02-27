import logging

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings
from async_fastapi_jwt_auth import AuthJWT

from logging import config as logging_config

from core.logger import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent.parent

logging_config.dictConfig(LOGGING)

load_dotenv(f"{BASE_DIR}/.env")


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias='REDIS_HOST')
    port: int = Field(validation_alias='REDIS_PORT')


class PostgreSQLSettings(BaseSettings):
    dbname: str = Field(validation_alias='DB_NAME')
    user: str = Field(validation_alias='DB_USER')
    password: str = Field(validation_alias='DB_PASSWORD')
    host: str = Field(validation_alias='DB_HOST')
    port: int = Field(validation_alias='DB_PORT')

    def get_db_url(self):
        dsn = f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'
        return dsn


class Settings(BaseSettings):
    log_level: int | str = Field(validation_alias='LOG_LEVEL', default=logging.DEBUG)
    redis: RedisSettings = RedisSettings()
    db: PostgreSQLSettings = PostgreSQLSettings()


settings = Settings()


class JWTSettings(BaseModel):
    authjwt_secret_key: str = 'secret'
    authjwt_token_location: set = {'cookies'}
    authjwt_token_csrf_protect: bool = False
