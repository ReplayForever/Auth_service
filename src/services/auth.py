from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import User
from sqlalchemy import select
from werkzeug.security import check_password_hash
from models.users import UserLogin


class AuthService:
    def __init__(self, redis: Redis, db: AsyncSession, jwt: AuthJWT):
        self.redis = redis
        self.db = db
        self.jwt = jwt

    async def get_by_login(self, login: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.login == login)
        )
        user = result.scalars().first()
        return user if user else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()
        return user if user else None

    async def check_password(self, user: UserLogin) -> bool:
        result = await self.db.execute(
            select(User.password).where(User.login == user.login)
        )
        password_hash = result.scalars().first()
        result = check_password_hash(password_hash, user.password)
        return bool(result)


@lru_cache()
def get_auth_service(
        redis: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends()
) -> AuthService:
    return AuthService(redis, db, jwt)
