import time
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, Request, HTTPException
from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from services.abstract import PostAbstractService
from models.schemas import User, LoginHistory, Token
from db.postgres import get_session
from db.redis import get_redis


class RefreshService(PostAbstractService):
    def __init__(self, authorize: AuthJWT, db: AsyncSession, redis_token: Redis):
        self._authorize = authorize
        self._db = db
        self._redis_token = redis_token

    async def find_user_role_id(self, user_id: str):
        result = await self._db.execute(select(User).where(User.id == user_id))
        user_row = result.fetchone()
        if user_row:
            user = user_row[0]
            role_id = user.role_id
        else:
            raise Exception("Please login again")
        return role_id

    async def find_user_agents(self, user_id: str):
        result = await self._db.execute(select(LoginHistory.user_agent).where(LoginHistory.user_id == user_id))
        history_rows = result.fetchall()
        user_agents = []
        if history_rows:
            for row in history_rows:
                user_agents.append(row)
        else:
            raise "User-Agent not found"
        return user_agents

    @staticmethod
    async def find_current_user_agent(request: Request):
        current_user_agent = request.headers.get("User-Agent")
        return current_user_agent

    async def update_refresh_token_in_db(self, refresh_token: str, new_refresh_token: str):
        await self._db.execute(
            update(Token)
            .where(Token.refresh_token == refresh_token)
            .values(refresh_token=new_refresh_token)
        )
        await self._db.commit()

    async def post(self, request: Request):
        await self._authorize.jwt_refresh_token_required()

        access_token = request.cookies.get('access_token_cookie')
        refresh_token = request.cookies.get('refresh_token_cookie')

        access_jti = await self._authorize.get_jti(access_token)
        refresh_jti = await self._authorize.get_jti(refresh_token)

        if await self._redis_token.exists(access_jti) or await self._redis_token.exists(refresh_jti):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Access and refresh tokens are invalid")
        
        user_id = await self._authorize.get_jwt_subject()
        role_id = await self.find_user_role_id(user_id)

        user_agents = await self.find_user_agents(user_id)

        user_agents = [row[0] for row in user_agents]
        current_user_agent = await self.find_current_user_agent(request)
        if current_user_agent in user_agents:
            access_token_exp = (await self._authorize.get_raw_jwt(access_token))["exp"]
            refresh_token_exp = (await self._authorize.get_raw_jwt(refresh_token))["exp"]
            
            access_token_ttl = access_token_exp - int(time.time())
            refresh_token_ttl = refresh_token_exp - int(time.time())

            await self._redis_token.set(name=access_jti, value=user_id, ex=access_token_ttl)
            await self._redis_token.set(name=refresh_jti, value=user_id, ex=refresh_token_ttl)

            new_access_token = await self._authorize.create_access_token(subject=user_id,
                                                                         user_claims={"role_id": role_id})
            new_refresh_token = await self._authorize.create_refresh_token(subject=user_id)

            await self._authorize.set_access_cookies(new_access_token)
            await self._authorize.set_refresh_cookies(new_refresh_token)

            await self.update_refresh_token_in_db(refresh_token=refresh_token, new_refresh_token=new_refresh_token)

            if not new_access_token and not new_refresh_token:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Error during refresh tokens')

        else:
            raise Exception("Please login again")


@lru_cache()
def get_refresh_service(
        authorize: AuthJWT = Depends(),
        db: AsyncSession = Depends(get_session),
        redis_token: Redis = Depends(get_redis),
) -> RefreshService:
    return RefreshService(authorize, db, redis_token)
