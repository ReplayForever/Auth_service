from functools import lru_cache

from fastapi import Depends
from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.abstract import PostAbstractService
from models.schemas import User
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
            raise "Юзер не найден"
        return role_id

    async def post(self):
        await self._authorize.jwt_refresh_token_required()

        user_id = await self._authorize.get_jwt_subject()
        role_id = await self.find_user_role_id(user_id)

        new_access_token = await self._authorize.create_access_token(subject=user_id, user_claims={"role_id": role_id})
        new_refresh_token = await self._authorize.create_refresh_token(subject=user_id)

        await self._authorize.set_access_cookies(new_access_token)
        await self._authorize.set_refresh_cookies(new_refresh_token)


@lru_cache()
def get_refresh_service(
        authorize: AuthJWT = Depends(),
        db: AsyncSession = Depends(get_session)
) -> RefreshService:
    return RefreshService(authorize, db)
