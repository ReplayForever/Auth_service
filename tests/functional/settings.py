from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")


class TestRedisSettings(BaseSettings):
    host: str = Field(validation_alias='REDIS_HOST')
    port: int = Field(validation_alias='REDIS_PORT')


class TestPostgresSettings(BaseSettings):
    dbname: str = Field(validation_alias='DB_NAME')
    user: str = Field(validation_alias='DB_USER')
    password: str = Field(validation_alias='DB_PASSWORD')
    host: str = Field(validation_alias='DB_HOST')
    port: int = Field(validation_alias='DB_PORT')

    def url(self):
        dsn = f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'
        return dsn


class TestFastAPISettings(BaseSettings):
    host: str = Field(validation_alias='FASTAPI_HOST', default='localhost')
    port: int = Field(validation_alias='FASTAPI_PORT', default=82)

    def url(self):
        return f'http://{self.host}:{self.port}/api/v1'


class TestSettings(BaseSettings):
    redis: TestRedisSettings = TestRedisSettings()
    postgres: TestPostgresSettings = TestPostgresSettings()
    fastapi: TestFastAPISettings = TestFastAPISettings()


settings = TestSettings()
