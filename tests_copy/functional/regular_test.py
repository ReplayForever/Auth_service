import psycopg2
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")

class TestPostgresSettings(BaseSettings):
    dbname: str = Field(validation_alias='DB_NAME')
    user: str = Field(validation_alias='DB_USER')
    password: str = Field(validation_alias='DB_PASSWORD')
    host: str = Field(validation_alias='DB_HOST')
    port: int = Field(validation_alias='DB_PORT')

    def dsn(self):
        return f"dbname={self.dbname} user={self.user} password={self.password} host={self.host} port={self.port}"

class TestSettings(BaseSettings):
    postgres: TestPostgresSettings = TestPostgresSettings()

settings = TestSettings()

def delete_user():
        conn = psycopg2.connect(
            dbname=settings.postgres.dbname,
            user=settings.postgres.user,
            password=settings.postgres.password,
            host=settings.postgres.host,
            port=settings.postgres.port
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE login = %s", ("testlogin",))
        conn.commit()

delete_user()
