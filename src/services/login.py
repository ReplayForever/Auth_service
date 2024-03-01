from functools import lru_cache

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.postgres import get_session
from models.schemas import User, LoginHistory, Token
from sqlalchemy import select
from werkzeug.security import check_password_hash
from models.users import UserLogin
from services.abstract import AbstractService
from async_fastapi_jwt_auth import AuthJWT


class LoginService(AbstractService):
    def __init__(self, db: AsyncSession, authorize: AuthJWT):
        self._db = db
        self._authorize = authorize

    async def get_data(self, user: UserLogin, user_agent: str):
        user_found = await self.get_by_login(user.login)
        if not user_found:
            return None
        await self.check_password(user)
        refresh_token = await self._authorize.create_refresh_token(subject=str(user_found.id))
        access_token = await self._authorize.create_access_token(subject=str(user_found.id),
                                                                 user_claims={'role_id': user_found.role_id})

        await self._authorize.set_access_cookies(access_token)
        await self._authorize.set_refresh_cookies(refresh_token)

        await self.set_by_login_history(user_id=user_found.id, user_agent=user_agent)
        await self.set_refresh_token(user_id=user_found.id, user_agent=user_agent,
                                     refresh_token=refresh_token)

        if not refresh_token and not access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка при логине")

    async def get_by_login(self, login: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.login == login)
        )
        user = result.scalars().first()
        return user if user else None

    async def check_password(self, user: UserLogin) -> bool:
        result = await self._db.execute(
            select(User.password).where(User.login == user.login)
        )
        password_hash = result.scalars().first()
        result = check_password_hash(password_hash, user.password)
        return bool(result)

    async def set_by_login_history(self, user_id: str, user_agent: str):
        history = LoginHistory(user_id=user_id, user_agent=user_agent)
        self._db.add(history)
        await self._db.commit()

    async def set_refresh_token(self, user_id: str, user_agent: str, refresh_token: str):
        token = Token(user_id=user_id, user_agent=user_agent, refresh_token=refresh_token)
        self._db.add(token)
        await self._db.commit()


@lru_cache()
def get_login_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
) -> LoginService:
    return LoginService(db, authorize)
