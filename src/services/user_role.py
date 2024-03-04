import datetime
from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from db.postgres import get_session
from db.redis import get_redis
from models.roles import RoleAssign, UserRole, RoleInDB
from models.schemas import Role, User
from models.users import UserProfileResult
from services.abstract import PostAbstractService, AbstractService
from services.common.roles_common import RolesCommon
from services.common.access_check_common import AccessCheckCommon


class UpdateUserRoleService(PostAbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def post(self, request: Request, role_assign: RoleAssign) -> UserRole:
        await self.check_access()
        await self.check_auth()

        role = await self._db.get(Role, role_assign.role_id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")
        user = await self._db.get(User, role_assign.user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        user.role_id = role_assign.role_id
        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)

        return UserRole(user=UserProfileResult(**user.__dict__), role=RoleInDB(**role.__dict__))


class GetUserRoleService(AbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def get_data(self, request: Request, user_id) -> RoleInDB:
        await self.check_access()

        user = await self._db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        role = await self._db.get(Role, user.role_id)

        return RoleInDB(**role.__dict__)


@lru_cache()
def update_user_role_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> UpdateUserRoleService:
    return UpdateUserRoleService(db, authorize, redis_token)


@lru_cache()
def get_user_role_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> GetUserRoleService:
    return GetUserRoleService(db, authorize, redis_token)
