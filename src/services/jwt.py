import json
from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Request, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from db.redis import get_redis
from models.tokens import AccessTokenInDB
from models.schemas import Token, User


class JWTService:
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.authorize = authorize
        self.redis = redis

    async def create_access_token(self, user_id: str) -> str:
        try:
            access_token = await self.authorize.create_access_token(subject=user_id)
            return access_token
        except Exception as e:
            raise f'Ошибка: {e}'

    async def create_refresh_token(self, user_id: str) -> str:
        try:
            refresh_token = await self.authorize.create_refresh_token(subject=user_id)
            return refresh_token
        except Exception as e:
            raise f'Ошибка: {e}'

    @staticmethod
    async def get_user_agent(request: Request) -> str:
        user_agent = request.headers.get("User-Agent")
        return user_agent

    async def set_access_token(self, token: str, user_id: str, role_id: int, expires_time: int):
        value = {"user_id": user_id, "role_id": role_id}
        value = json.dumps(value)
        await self.redis.set(name=token, value=value, ex=expires_time)

    async def set_refresh_token(self, token: str, user_agent: str):
        new_token = Token(refresh_token=token, user_agent=user_agent)
        self.db.add(new_token)
        await self.db.commit()

    async def get_access_token(self, user_id: str):
        try:
            if not await self.redis.exists(user_id):
                return None

            token = await self.redis.get(name=user_id)
            return token
        except Exception as e:
            raise f'Ошибка {e}'


async def get_refresh_token(self, user_id: str) -> AccessTokenInDB:
    try:
        stmt = select(Token).join(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        token = result.scalars().first()
        if token is None:
            return None
        return token
    except Exception as e:
        raise f'Ошибка {e}'


@lru_cache()
def get_jwt_service(
        redis: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends()
) -> JWTService:
    return JWTService(db, authorize, redis)
