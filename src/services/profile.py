import datetime
from functools import lru_cache


from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from werkzeug.security import generate_password_hash

from db.postgres import get_session
from models.schemas import User, LoginHistory
from models.users import UserProfileResult, UserChangePassword, ChangeUserProfile, UserProfileHistory, Paginator
from services.abstract import AbstractService, PatchAbstractService
from utils.validators import validate_password


class ProfileInfoService(AbstractService):
    def __init__(self, db: AsyncSession, authorize: AuthJWT):
        self._db = db
        self._authorize = authorize

    async def get_data(self) -> UserProfileResult:
        await self._authorize.jwt_required()

        user_id = await self._authorize.get_jwt_subject()
        user = await self._db.get(User, user_id)
        return UserProfileResult(**user.__dict__)


class ProfileHistoryService(AbstractService):
    def __init__(self, db: AsyncSession, authorize: AuthJWT):
        self._db = db
        self._authorize = authorize

    async def get_data(self, token, page, limit) -> Paginator:
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Page not found')
        elif not history_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='History not found')

        return Paginator(page=page, limit=limit, results=history_list)
#
#
# class ProfileUpdateInfoService(PatchAbstractService):
#     def __init__(self, db: AsyncSession, jwt: JWT):
#         self._db = db
#         self._jwt = jwt
#
#     async def patch(self, token, user_info: ChangeUserProfile) -> UserProfileResult:
#         token_info = await self._jwt.get_access_token(token)
#         user = await self._db.get(User, token_info['user_id'])
#
#         for attr, value in user_info.dict().items():
#             if value:
#                 setattr(user, attr, value)
#
#         user.modified_at = datetime.datetime.now()
#
#         await self._db.commit()
#         await self._db.refresh(user)
#         return UserProfileResult(**user.__dict__)
#
#
# class UpdatePasswordService(PatchAbstractService):
#     def __init__(self, db: AsyncSession, jwt: JWT):
#         self._db = db
#         self._jwt = jwt
#
#     async def patch(self, token, passwords: UserChangePassword) -> None:
#         token_info = await self._jwt.get_access_token(token)
#         user = await self._db.get(User, token_info['user_id'])
#
#         if not user.check_password(passwords.password):
#             raise HTTPException(status_code=400, detail='Wrong password')
#         elif not validate_password(passwords.new_password):
#             raise HTTPException(status_code=400, detail='Password too simple')
#
#         user.password = generate_password_hash(passwords.new_password)
#         user.modified_at = datetime.datetime.now()
#
#         await self._db.commit()
#         await self._db.refresh(user)
#
#


@lru_cache()
def get_profile_info_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
) -> ProfileInfoService:
    return ProfileInfoService(db, authorize)
#
#
# @lru_cache()
# def get_profile_history_service(
#         db: AsyncSession = Depends(get_session),
#         jwt: JWT = Depends(get_jwt),
# ) -> ProfileHistoryService:
#     return ProfileHistoryService(db, jwt)
#
#
# @lru_cache()
# def patch_profile_info_service(
#         db: AsyncSession = Depends(get_session),
#         jwt: JWT = Depends(get_jwt),
# ) -> ProfileUpdateInfoService:
#     return ProfileUpdateInfoService(db, jwt)
#
#
# @lru_cache()
# def update_password_service(
#         db: AsyncSession = Depends(get_session),
#         jwt: JWT = Depends(get_jwt),
# ) -> UpdatePasswordService:
#     return UpdatePasswordService(db, jwt)
