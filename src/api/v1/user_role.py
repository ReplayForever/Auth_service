from typing import Annotated

from fastapi import APIRouter, Cookie, Depends
from starlette import status

from models.roles import RoleAssign, UserRole
from models.users import UserError
from services.user_role import UpdateUserRoleService, update_user_role_service

router = APIRouter()


@router.get("/user_role/{user_id}/", description="Получение информации о роли")
async def get_user_role(user_id: str, access_token: Annotated[str | None, Cookie()]) -> UserRole:
    return None


@router.post("/user_role/",
             description="Назначение роли",
             status_code=status.HTTP_201_CREATED,
             response_model=UserRole,
             responses={status.HTTP_401_UNAUTHORIZED: {'model': UserError},
                        status.HTTP_404_NOT_FOUND: {'model': UserError},
                        status.HTTP_503_SERVICE_UNAVAILABLE: {'model': UserError}})
async def assign_role(role_assign: RoleAssign,
                      access_token: Annotated[str | None, Cookie()] = None,
                      update_role: UpdateUserRoleService = Depends(update_user_role_service)) -> UserRole:
    answer = await update_role.post(access_token, role_assign)
    return answer
