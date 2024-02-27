import datetime
from functools import lru_cache

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.postgres import get_session
from models.roles import RoleAssign, UserRole, RoleInDB
from models.schemas import Role, User
from models.users import UserProfileResult
from services.abstract import PostAbstractService
from services.jwt import JWT, get_jwt


class UpdateUserRoleService(PostAbstractService):
    def __init__(self, db: AsyncSession, jwt: JWT):
        self._db = db
        self._jwt = jwt

    async def post(self, token, role_assign: RoleAssign) -> UserRole:
        token_info = await self._jwt.get_access_token(token)
        user_role = await self._db.get(Role, token_info['role_id'])
        if not user_role.is_superuser and not user_role.is_manager and not user_role.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        role = await self._db.get(Role, role_assign.role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        user = await self._db.get(User, role_assign.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.role_id = role_assign.role_id
        user.modified_at = datetime.datetime.now()

        await self._db.commit()
        await self._db.refresh(user)

        return UserRole(user=UserProfileResult(**user.__dict__), role=RoleInDB(**role.__dict__))


@lru_cache()
def update_user_role_service(
        db: AsyncSession = Depends(get_session),
        jwt: JWT = Depends(get_jwt),
) -> UpdateUserRoleService:
    return UpdateUserRoleService(db, jwt)
