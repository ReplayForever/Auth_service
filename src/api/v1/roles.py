from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from models.roles import RoleInDB, CreateRole, RoleDelete, RoleChangePermission, RoleError
from services.roles import (RoleGetService, RoleCreateService,
                            RoleDeleteService, RoleUpdateService, get_role_get_service,
                            get_role_create_service, get_role_delete_service, get_role_update_service)

router = APIRouter()

@router.get('/roles/',
            description="Получение списка ролей",
            response_model=list[RoleInDB],
            responses={status.HTTP_400_BAD_REQUEST:{"model": RoleError},
                        status.HTTP_403_FORBIDDEN:{"model": RoleError}})
async def get_roles(access_token: Annotated[str | None, Cookie()] = None,
                    role_service: RoleGetService = Depends(get_role_get_service)) -> list[RoleInDB]:
    answer = await role_service.get_data(access_token)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка при получении списка ролей")


@router.post("/roles/",
              description="Создание роли",
              response_model=RoleInDB,
                responses={status.HTTP_400_BAD_REQUEST:{"model": RoleError},
                           status.HTTP_403_FORBIDDEN:{"model": RoleError}})
async def create_role(role: CreateRole,
                      access_token: Annotated[str | None, Cookie()] = None,
                      role_service: RoleCreateService = Depends(get_role_create_service)) -> RoleInDB:
    answer = await role_service.create(role, access_token)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка при создании роли")


@router.delete("/roles/",
                description="Удаление роли",
                responses={status.HTTP_400_BAD_REQUEST:{"model": RoleError},
                           status.HTTP_403_FORBIDDEN:{"model": RoleError},
                           status.HTTP_404_NOT_FOUND: {"model": RoleError}})
async def delete_role(role: RoleDelete,
                      access_token: Annotated[str | None, Cookie()] = None,
                      role_service: RoleDeleteService = Depends(get_role_delete_service)) -> None:
    answer = await role_service.delete(role.id, access_token)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка при удалении роли")


@router.patch("/roles/",
               description="Изменение прав роли",
               response_model=RoleInDB,
                responses={status.HTTP_400_BAD_REQUEST:{"model": RoleError},
                           status.HTTP_403_FORBIDDEN:{"model": RoleError},
                           status.HTTP_404_NOT_FOUND: {"model": RoleError}})
async def update_role(role: RoleChangePermission,
                      access_token: Annotated[str | None, Cookie()] = None,
                      role_service: RoleUpdateService = Depends(get_role_update_service)) -> RoleInDB:
    answer = await role_service.patch(role.role_id, role, access_token)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка при изменении прав роли")
    