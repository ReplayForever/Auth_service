from typing import Annotated

from fastapi import APIRouter, Cookie

from models.roles import CreateRole, RoleInDB, RoleDelete, RoleChangePermission

router = APIRouter()


@router.post("/roles/",
              description="Создание роли")
async def create_role(role: CreateRole, access_token: Annotated[str | None, Cookie()]) -> RoleInDB:
    return None


@router.get("/roles/",
             description="Получение списка ролей")
async def get_roles(access_token: Annotated[str | None, Cookie()]) -> list[RoleInDB]:
    return None


@router.delete("/roles/",
                description="Удаление роли")
async def delete_role(role: RoleDelete, access_token: Annotated[str | None, Cookie()]) -> None:
    return None


@router.patch("/roles/",
               description="Изменение прав роли")
async def update_role(role: RoleChangePermission, access_token: Annotated[str | None, Cookie()]) -> RoleInDB:
    return None
