import json
from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Request, HTTPException, Depends
from redis import exceptions
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from db.redis import get_redis
from models.tokens import AccessTokenInDB
from models.schemas import Token, User


class JWT:
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.authorize = authorize
        self.redis = redis

    async def create_access_token(self, user_id: str) -> str:
        try:
            access_token = await self.authorize.create_access_token(subject=user_id)
            return access_token
        except Exception as e:
            raise HTTPException(status_code=404, detail="User not found")

    async def create_refresh_token(self, user_id: str) -> str:
        try:
            refresh_token = await self.authorize.create_refresh_token(subject=user_id)
            return refresh_token
        except Exception as e:
            raise HTTPException(status_code=404, detail='User not found')

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

    async def get_access_token(self, token: str):
        try:
            if not await self.redis.exists(token):
                raise HTTPException(status_code=404, detail="User not found in Redis")

            user_id = await self.redis.get(name=token)
            return json.loads(user_id)

        except exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="Unable to connect to Redis")


async def get_refresh_token(self, user_id: str) -> AccessTokenInDB:
    try:
        stmt = select(Token).join(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        token = result.scalars().first()
        if token is None:
            raise HTTPException(status_code=404, detail="Token not found for the user")
        return token
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")


@lru_cache()
def get_jwt(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis: Redis = Depends(get_redis),
) -> JWT:
    return JWT(db, authorize, redis)