from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from models.roles import CreateRole, RoleDelete, RoleChangePermission, RoleError, RoleToRepresentation
from models.users import UserMessageOut
from services.roles import (RoleGetService, RoleCreateService,
                            RoleDeleteService, RoleUpdateService, get_role_get_service,
                            get_role_create_service, get_role_delete_service, get_role_update_service)

router = APIRouter()


@router.get('/roles/',
            description="Получение списка ролей",
            response_model=list[RoleToRepresentation],
            responses={status.HTTP_400_BAD_REQUEST: {"model": RoleError},
                        status.HTTP_403_FORBIDDEN: {"model": RoleError}})
async def get_roles(
        request: Request,
        role_service: RoleGetService = Depends(get_role_get_service)
) -> list[RoleToRepresentation]:
    answer = await role_service.get_data(request)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка при получении списка ролей")


@router.post("/roles/",
             description="Создание роли",
             response_model=RoleToRepresentation,
             responses={status.HTTP_400_BAD_REQUEST: {"model": RoleError},
                        status.HTTP_403_FORBIDDEN: {"model": RoleError}})
async def create_role(request: Request,
                      role: CreateRole,
                      role_service: RoleCreateService = Depends(get_role_create_service)) -> RoleToRepresentation:
    answer = await role_service.create(role, request)
    return answer


@router.delete("/roles/",
               description="Удаление роли",
               response_model=UserMessageOut,
               responses={status.HTTP_400_BAD_REQUEST: {"model": RoleError},
                          status.HTTP_403_FORBIDDEN: {"model": RoleError},
                          status.HTTP_404_NOT_FOUND: {"model": RoleError}})
async def delete_role(role: RoleDelete,
                      request: Request,
                      role_service: RoleDeleteService = Depends(get_role_delete_service)) -> UserMessageOut:
    await role_service.delete(role.id, request)
    return UserMessageOut(message="Role deleted successfully")


@router.patch("/roles/",
              description="Изменение прав роли",
              response_model=RoleToRepresentation,
              responses={status.HTTP_400_BAD_REQUEST: {"model": RoleError},
                         status.HTTP_403_FORBIDDEN: {"model": RoleError},
                         status.HTTP_404_NOT_FOUND: {"model": RoleError}})
async def update_role(role: RoleChangePermission,
                      request: Request,
                      role_service: RoleUpdateService = Depends(get_role_update_service)) -> RoleToRepresentation:
    answer = await role_service.patch(role.role_id, role, request)
    return answer
