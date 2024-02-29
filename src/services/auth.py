from functools import lru_cache
import uuid

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, Request
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from werkzeug.security import check_password_hash

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import User, Role, LoginHistory, Token
from models.users import UserCreate, UserLogin, UserSuccessLogin
from services.abstract import AbstractService, DeleteAbstractService


class SignUpService(AbstractService):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_data(self, user_create: UserCreate):
        user = User(**jsonable_encoder(user_create))

        try:
            result = await self._db.execute(select(Role).where(
                Role.is_admin == False,
                Role.is_subscriber == False,
                Role.is_superuser == False,
                Role.is_manager == False
            ))
            role = result.fetchone()
            if role is None:
                raise NoResultFound('Нет такой роли')
        except NoResultFound:
            unique_name = str(uuid.uuid4())
            role = Role(name=unique_name,
                        description="Base user role",
                        is_admin=False,
                        is_superuser=False,
                        is_subscriber=False,
                        is_manager=False)
            self._db.add(role)
            await self._db.commit()
            await self._db.refresh(role)
        
        user.role_id = role[0].id
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        
        return user


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

    async def set_refresh_token(self, user_id: str, user_agent: str, refresh_token: str):
        token = Token(user_id=user_id, user_agent=user_agent, refresh_token=refresh_token)
        self._db.add(token)
        await self._db.commit()


class LogoutService(DeleteAbstractService):
    def __init__(self, authorize: AuthJWT,
                 redis_token: Redis,
                 db: AsyncSession):
        self._authorize = authorize
        self._redis_token = redis_token
        self._db = db

    async def delete(self, request: Request):
        await self._authorize.jwt_required()

        jwt_subject = await self._authorize.get_jwt_subject()
        access_token = request.cookies.get('access_token_cookie')
        refresh_token = request.cookies.get('refresh_token_cookie')

        await self._authorize.unset_jwt_cookies()

        await self._redis_token.set(name=access_token, value=jwt_subject, ex=900)
        await self.delete_refresh_token_from_db(refresh_token)

    async def delete_refresh_token_from_db(self, refresh_token: str):
        token_to_delete = await self._db.execute(select(Token).where(Token.refresh_token == refresh_token))
        token = token_to_delete.fetchone()
        if token:
            await self._db.delete(token[0])
            await self._db.commit()
        else:
            raise Exception('Токен не найден')


@lru_cache()
def get_login_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
) -> LoginService:
    return LoginService(db, authorize)


@lru_cache()
def get_sign_up_service(
        db: AsyncSession = Depends(get_session),
) -> SignUpService:
    return SignUpService(db)


@lru_cache()
def get_logout_service(
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
        db: AsyncSession = Depends(get_session)
) -> LogoutService:
    return LogoutService(authorize, redis_token, db)
