from functools import lru_cache

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import Token
from services.abstract import DeleteAbstractService


class LogoutService(DeleteAbstractService):
    def __init__(self, authorize: AuthJWT,
                 redis_token: Redis,
                 db: AsyncSession):
        self._authorize = authorize
        self._redis_token = redis_token
        self._db = db

    async def delete(self, request: Request):
        await self._authorize.jwt_required()

        jwt_subject = await self._authorize.get_jwt_subject()
        access_token = request.cookies.get('access_token_cookie')
        refresh_token = request.cookies.get('refresh_token_cookie')

        await self._authorize.unset_jwt_cookies()

        await self._redis_token.set(name=access_token, value=jwt_subject, ex=900)
        await self.delete_refresh_token_from_db(refresh_token)

    async def delete_refresh_token_from_db(self, refresh_token: str):
        token_to_delete = await self._db.execute(select(Token).where(Token.refresh_token == refresh_token))
        token = token_to_delete.fetchone()
        if token:
            await self._db.delete(token[0])
            await self._db.commit()
        else:
            raise Exception('Токен не найден')


@lru_cache()
def get_logout_service(
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_session)
) -> LogoutService:
    return LogoutService(authorize, redis_token, db)
