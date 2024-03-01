from functools import lru_cache

from fastapi import Depends, Request
from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.users import UserSuccessRefreshToken
from services.abstract import PostAbstractService
from models.schemas import User, LoginHistory, Token
from db.postgres import get_session


class RefreshService(PostAbstractService):
    def __init__(self, authorize: AuthJWT, db: AsyncSession):
        self._authorize = authorize
        self._db = db

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

    async def update_refresh_token_in_db(self, user_id: str, new_refresh_token: str):
        await self._db.execute(
            update(Token).where(
                Token.user_id == user_id
            ).values(refresh_token=new_refresh_token)
        )
        await self._db.commit()

    async def post(self, request: Request):
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()
        role_id = await self.find_user_role_id(user_id)

        user_agents = await self.find_user_agents(user_id)

        user_agents = [row[0] for row in user_agents]
        current_user_agent = await self.find_current_user_agent(request)
        if current_user_agent in user_agents:
            new_access_token = await self._authorize.create_access_token(subject=user_id, user_claims={"role_id": role_id})
            new_refresh_token = await self._authorize.create_refresh_token(subject=user_id)

            await self._authorize.set_access_cookies(new_access_token)
            await self._authorize.set_refresh_cookies(new_refresh_token)

            await self.update_refresh_token_in_db(user_id, new_refresh_token)

            return UserSuccessRefreshToken(access_token=new_access_token, refresh_token=new_refresh_token)
        else:
            raise Exception("Please login again")


@lru_cache()
def get_refresh_service(
        authorize: AuthJWT = Depends(),
        db: AsyncSession = Depends(get_session)
) -> RefreshService:
    return RefreshService(authorize, db)
