from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")


class TestRedisSettings(BaseSettings):
    host: str = Field(validation_alias='REDIS_HOST')
    port: int = Field(validation_alias='REDIS_PORT')


class UtilsSettings(BaseSettings):
    redis: TestRedisSettings = TestRedisSettings()


settings = UtilsSettings()
