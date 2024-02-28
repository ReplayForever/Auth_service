from functools import lru_cache

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis

from db.redis import get_redis
from services.abstract import DeleteAbstractService


class LogoutService(DeleteAbstractService):
    def __init__(self, authorize: AuthJWT,
                 redis_token: Redis,):
        self._authorize = authorize
        self._redis_token = redis_token

    async def delete(self, request: Request):
        await self._authorize.jwt_required()

        jwt_subject = await self._authorize.get_jwt_subject()
        access_token = request.cookies.get('access_token_cookie')

        await self._authorize.unset_jwt_cookies()

        await self._redis_token.set(name=access_token, value=jwt_subject, ex=10)


@lru_cache()
def get_logout_service(
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> LogoutService:
    return LogoutService(authorize, redis_token)
