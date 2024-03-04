import datetime
from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import User, LoginHistory
from models.users import UserProfileResult, UserChangePassword, ChangeUserProfile, UserProfileHistory, Paginator
from services.abstract import AbstractService, PatchAbstractService
from services.common.access_check_common import AccessCheckCommon
from utils.validators import validate_password


class ProfileInfoService(AbstractService, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def get_data(self) -> UserProfileResult:
        await self.check_access()
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()
        user = await self._db.get(User, user_id)
        return UserProfileResult(**user.__dict__)


class ProfileHistoryService(AbstractService, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def get_data(self, page, limit) -> Paginator:
        await self.check_access()
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()

        history = await self._db.execute(
            select(LoginHistory).offset((page-1)*limit).limit(limit).where(
                LoginHistory.user_id == user_id
            )
        )

        history_list = []
        for login_history in history.fetchall():
            history_list.append(UserProfileHistory(**login_history[0].__dict__))

        if not history_list and page > 1:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Page not found')
        elif not history_list:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='History not found')

        return Paginator(page=page, limit=limit, results=history_list)


class ProfileUpdateInfoService(PatchAbstractService, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def patch(self, user_info: ChangeUserProfile) -> UserProfileResult:
        await self.check_access()
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()
        user = await self._db.get(User, user_id)

        for attr, value in user_info.dict().items():
            if value:
                setattr(user, attr, value)

        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)
        return UserProfileResult(**user.__dict__)


class UpdatePasswordService(PatchAbstractService, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def patch(self, passwords: UserChangePassword) -> None:
        await self.check_access()
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()
        user = await self._db.get(User, user_id)

        if not user.check_password(passwords.password):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Wrong password')
        elif not validate_password(passwords.new_password):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Password too simple')

        user.password = generate_password_hash(passwords.new_password)
        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)


@lru_cache()
def get_profile_info_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> ProfileInfoService:
    return ProfileInfoService(db, authorize, redis_token)


@lru_cache()
def get_profile_history_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> ProfileHistoryService:
    return ProfileHistoryService(db, authorize, redis_token)


@lru_cache()
def patch_profile_info_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> ProfileUpdateInfoService:
    return ProfileUpdateInfoService(db, authorize, redis_token)


@lru_cache()
def update_password_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> UpdatePasswordService:
    return UpdatePasswordService(db, authorize, redis_token)
