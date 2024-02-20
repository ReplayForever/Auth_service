import json

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from db.redis import get_redis
from models.tokens import AccessTokenInDB
from models.schemas import Token, User
from functools import lru_cache


class JWTService:
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.authorize = authorize
        self.redis = redis

    async def access_token_loop(self, user_id: str, role_id: int, expires_time: int):
        token = await self.get_access_token(user_id)
        if not token:
            access_token = await self.create_access_token(user_id)
            await self.set_access_token(access_token, user_id, role_id, expires_time)

    async def refresh_token_loop(self, user_id: str, user_agent: str):
        token = await self.get_refresh_token(user_id)
        if not token:
            refresh_token = await self.create_refresh_token(user_id)
            await self.set_refresh_token(refresh_token, user_agent)

    async def create_access_token(self, user_id: str) -> str:
        access_token = await self.authorize.create_access_token(subject=user_id)
        return access_token

    async def create_refresh_token(self, user_id: str) -> str:
        refresh_token = await self.authorize.create_refresh_token(subject=user_id)
        return refresh_token

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
        token = await self.redis.get(name=user_id)
        return token

    async def get_refresh_token(self, user_id: str) -> AccessTokenInDB:
        stmt = select(Token).join(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        token = result.scalars().first()
        return token


@lru_cache()
def get_token_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis: Redis = Depends(get_redis)
) -> JWTService:
    return JWTService(db, authorize, redis)
