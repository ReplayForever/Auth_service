from http import HTTPStatus

from fastapi import HTTPException

from models.schemas import Role


class RolesCommon:
    _authorize = None
    _db = None

    async def check_auth(self):
        await self._authorize.jwt_required()

        role_id = (await self._authorize.get_raw_jwt())["role_id"]

        role = await self._db.get(Role, role_id)
        if not (role.is_admin or role.is_manager or role.is_superuser):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail="Only admins, moderators, and superusers can get all roles")
