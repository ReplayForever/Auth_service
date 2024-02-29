from contextlib import asynccontextmanager

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from fastapi import Request
from starlette.responses import JSONResponse

from api.v1 import auth, profile, user_role, roles
from core.config import settings, JWTSettings
from core.logger import LOGGING
from db import redis


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


app.include_router(auth.router, prefix='/api/v1', tags=['auth'])
app.include_router(profile.router, prefix='/api/v1', tags=['profile'])
app.include_router(roles.router, prefix='/api/v1', tags=['roles'])
app.include_router(user_role.router, prefix='/api/v1', tags=['user_role'])


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=settings.log_level
    )
