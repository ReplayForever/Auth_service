import datetime
from functools import lru_cache

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.schemas import Role
from models.roles import RoleInDB, CreateRole, RoleChangePermission
from services.abstract import AbstractService, PatchAbstractService, CreateAbstractService, DeleteAbstractService
from services.jwt import JWT, get_jwt


class RoleGetService(AbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def get_data(self, token: str) -> list[RoleInDB]:
        token_info = await self._jwt.get_access_token(token)
        role = await self._db.get(Role, token_info["role_id"])
        if not (role.is_admin or role.is_manager or role.is_superuser):
            raise HTTPException(status_code=403, detail="Only admins, moderators, and superusers can get all roles")
        
        roles = await self._db.execute(select(Role))
        return [RoleInDB(**role._mapping) for role in roles]


class RoleCreateService(CreateAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def create(self, role: CreateRole, token: str) -> RoleInDB:
        token_info = await self._jwt.get_access_token(token)
        role = await self._db.get(Role, token_info["role_id"])
        if not (role.is_admin or role.is_manager or role.is_superuser):
            raise HTTPException(status_code=403, detail="Only admins, moderators, and superusers can create roles")

        new_role = Role(**role.dict())
        self._db.add(new_role)
        await self._db.commit()
        await self._db.refresh(new_role)
        return RoleInDB(**new_role.__dict__)


class RoleDeleteService(DeleteAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def delete(self, role_id: int, token: str) -> None:
        token_info = await self._jwt.get_access_token(token)
        role = await self._db.get(Role, token_info["role_id"])
        if not (role.is_admin or role.is_manager or role.is_superuser):
            raise HTTPException(status_code=403, detail="Only admins, moderators, and superusers can delete roles")

        role = await self._db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        await self._db.delete(role)
        await self._db.commit()

        return {"message": "Role deleted successfully"}


class RoleUpdateService(PatchAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def patch(self, role_id: int, role_update: RoleChangePermission, token: str) -> RoleInDB:
        token_info = await self._jwt.get_access_token(token)
        role = await self._db.get(Role, token_info["role_id"])
        if not (role.is_admin or role.is_manager or role.is_superuser):
            raise HTTPException(status_code=403, detail="Only admins, moderators, and superusers can update roles")

        role = await self._db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        for field, value in role_update.dict(exclude_unset=True).items():
            setattr(role, field, value)

        role.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(role)
        return RoleInDB(**role.__dict__)


@lru_cache()
def get_role_create_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> RoleCreateService:
    return RoleCreateService(db, jwt)


@lru_cache()
def get_role_get_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> RoleGetService:
    return RoleGetService(db, jwt)


@lru_cache()
def get_role_delete_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> RoleDeleteService:
    return RoleDeleteService(db, jwt)


@lru_cache()
def get_role_update_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> RoleUpdateService:
    return RoleUpdateService(db, jwt)
