import datetime
from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import User
from models.users import UserProfileResult, UserChangePassword, ChangeUserProfile
from services.abstract import AbstractService, PatchAbstractService
from services.jwt import JWT, get_jwt
from utils.validators import validate_password


class ProfileInfoService(AbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def get_data(self, token) -> UserProfileResult:
        token_info = await self._jwt.get_access_token(token)

        user = await self._db.get(User, token_info['id'])
        return UserProfileResult(**user.__dict__)


class ProfileUpdateInfoService(PatchAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def patch(self, token, user_info: ChangeUserProfile) -> UserProfileResult:
        token_info = await self._jwt.get_access_token(token)
        user = await self._db.get(User, token_info['id'])

        for attr, value in user_info.dict().items():
            if value:
                setattr(user, attr, value)

        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)
        return UserProfileResult(**user.__dict__)


class UpdatePasswordService(PatchAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def patch(self, token, passwords: UserChangePassword) -> None:
        token_info = await self._jwt.get_access_token(token)
        user = await self._db.get(User, token_info['id'])

        if not user.check_password(passwords.password):
            raise HTTPException(status_code=400, detail='Wrong password')
        elif not validate_password(passwords.new_password):
            raise HTTPException(status_code=400, detail='Password too simple')

        user.password = generate_password_hash(passwords.new_password)
        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)


@lru_cache()
def get_profile_info_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> ProfileInfoService:
    return ProfileInfoService(db, jwt)


@lru_cache()
def patch_profile_info_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> ProfileUpdateInfoService:
    return ProfileUpdateInfoService(db, jwt)


@lru_cache()
def update_password_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> UpdatePasswordService:
    return UpdatePasswordService(db, jwt)
