import datetime
from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.requests import Request

from db.postgres import get_session
from db.redis import get_redis
from models.schemas import Role
from models.roles import CreateRole, RoleChangePermission, RoleToRepresentation
from services.abstract import AbstractService, PatchAbstractService, CreateAbstractService, DeleteAbstractService
from services.common.roles_common import RolesCommon
from services.common.access_check_common import AccessCheckCommon


class RoleGetService(AbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def get_data(self, request: Request) -> list[RoleToRepresentation]:
        await self.check_access()
        await self.check_auth()

        roles = await self._db.execute(select(Role))
        roles = roles.fetchall()
        return [RoleToRepresentation(**role[0].__dict__) for role in roles]


class RoleCreateService(CreateAbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def create(self, role: CreateRole, request: Request) -> RoleToRepresentation:
        await self.check_access()
        await self.check_auth()

        new_role = Role(**role.dict())
        self._db.add(new_role)
        try:
            await self._db.commit()
        except IntegrityError:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Role with name '%s' already exists" % new_role.name)
        await self._db.refresh(new_role)
        return RoleToRepresentation(**new_role.__dict__)


class RoleDeleteService(DeleteAbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def delete(self, role_id: int, request: Request) -> None:
        await self.check_access()
        await self.check_auth()

        role = await self._db.get(Role, role_id)

        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

        await self._db.delete(role)
        await self._db.commit()


class RoleUpdateService(PatchAbstractService, RolesCommon, AccessCheckCommon):
    def __init__(self, db: AsyncSession, authorize: AuthJWT, redis_token: Redis):
        self._db = db
        self._authorize = authorize
        self._redis_token = redis_token

    async def patch(self, role_id: int, role_update: RoleChangePermission, request: Request) -> RoleToRepresentation:
        await self.check_access()
        await self.check_auth()

        role = await self._db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Role not found")

        for field, value in role_update.dict(exclude_unset=True).items():
            setattr(role, field, value)

        role.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(role)
        return RoleToRepresentation(**role.__dict__)


@lru_cache()
def get_role_create_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> RoleCreateService:
    return RoleCreateService(db, authorize, redis_token)


@lru_cache()
def get_role_get_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> RoleGetService:
    return RoleGetService(db, authorize, redis_token)


@lru_cache()
def get_role_delete_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> RoleDeleteService:
    return RoleDeleteService(db, authorize, redis_token)


@lru_cache()
def get_role_update_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis_token: Redis = Depends(get_redis),
) -> RoleUpdateService:
    return RoleUpdateService(db, authorize, redis_token)
