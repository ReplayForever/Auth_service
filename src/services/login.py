from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.schemas import User, LoginHistory
from sqlalchemy import select
from werkzeug.security import check_password_hash
from models.users import UserLogin, UserSuccessLogin
from services.jwt import JWT, get_jwt
from services.abstract import AbstractService


class LoginService(AbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def get_data(self, user: UserLogin, user_agent: str):
        user_found = await self.get_by_login(user.login)
        if not user_found:
            return None
        await self.check_password(user)
        refresh_token = await self._jwt.create_refresh_token(user_found.id)
        access_token = await self._jwt.create_access_token(user_found.id)

        await self._jwt.authorize.set_access_cookies(access_token)
        await self._jwt.authorize.set_refresh_cookies(refresh_token)

        await self._jwt.set_refresh_token(refresh_token, user_agent=user_agent, user_id=user_found.id)
        # await self._jwt.set_access_token(access_token, str(user_found.id), user_found.role_id, 3600)

        await self.set_by_login_history(user_id=user_found.id, user_agent=user_agent)

        return UserSuccessLogin(refresh_token=refresh_token, access_token=access_token)

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


@lru_cache()
def get_login_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> LoginService:
    return LoginService(db, jwt)
