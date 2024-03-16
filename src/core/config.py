import logging

from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings

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
    echo: bool =Field(validation_alias='ECHO', default=True)

    def get_db_url(self):
        dsn = f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'
        return dsn


class YandexClientSettings(BaseSettings):
    client_id: str = Field(validation_alias='CLIENT_ID')
    client_secret: str = Field(validation_alias='CLIENT_SECRET')


class RateLimitSettings(BaseSettings):
    limit: int = Field(validation_alias='LIMIT', default=1000)
    interval: int = Field(validation_alias='INTERVAL', default=60)

class TracingSettings(BaseSettings):
    jaeger_agent_host: str = os.getenv('AGENT_HOST', 'jaeger')
    jaeger_agent_port: int = int(os.getenv('AGENT_PORT', '6831'))
    enable_tracer: bool = Field(validation_alias='ENABLE_TRACER', default=True)

class Settings(BaseSettings):
    log_level: int | str = Field(validation_alias='LOG_LEVEL', default=logging.DEBUG)

    redis: RedisSettings = RedisSettings()
    db: PostgreSQLSettings = PostgreSQLSettings()
    yandex: YandexClientSettings = YandexClientSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    tracing: TracingSettings = TracingSettings()


settings = Settings()


class JWTSettings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = False
    authjwt_cookie_csrf_protect: bool = False
