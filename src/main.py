from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import settings
from core.logger import LOGGING
from db import redis
from db.postgres import create_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)

    yield

    await redis.redis.close()

app = FastAPI(
    title='AUTH сервис',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description="Сервис, предоставляющий API для аутентификации и авторизации пользователей, "
                "позволяющий настроить их роли и права",
    version="1.0.0",
    lifespan=lifespan
)


@app.on_event("startup")
async def startup():
    from models.schemas import User, Role, LoginHistory
    await create_database()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=settings.log_level
    )
