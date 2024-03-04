from fastapi import APIRouter, Depends

from http import HTTPStatus
from starlette.requests import Request

from models.roles import RoleAssign, UserRole, RoleInDB
from models.users import UserError
from services.user_role import (UpdateUserRoleService, GetUserRoleService,
                                update_user_role_service, get_user_role_service)

router = APIRouter()


@router.get("/user_role/{user_id}/",
            description="Получение информации о роли",
            status_code=HTTPStatus.OK,
            response_model=RoleInDB,
            responses={HTTPStatus.UNAUTHORIZED: {'model': UserError},
                       HTTPStatus.NOT_FOUND: {'model': UserError},
                       HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
async def get_user_role(user_id: str,
                        request: Request,
                        get_role: GetUserRoleService = Depends(get_user_role_service)) -> RoleInDB:
    answer = await get_role.get_data(request, user_id)
    return answer


@router.post("/user_role/",
             description="Назначение роли",
             status_code=HTTPStatus.CREATED,
             response_model=UserRole,
             responses={HTTPStatus.UNAUTHORIZED: {'model': UserError},
                        HTTPStatus.NOT_FOUND: {'model': UserError},
                        HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
async def assign_role(role_assign: RoleAssign,
                      request: Request,
                      update_role: UpdateUserRoleService = Depends(update_user_role_service)) -> UserRole:
    answer = await update_role.post(request, role_assign)
    return answer
