from typing import Annotated

from fastapi import APIRouter, Cookie

from models.roles import RoleAssign, UserRole

router = APIRouter()


@router.get("/user_role/{user_id}/", description="Получение информации о роли")
async def get_user_role(user_id: str, access_token: Annotated[str | None, Cookie()]) -> UserRole:
    return None


@router.post("/user_role/", description="Назначение роли")
async def assign_role(role_assign: RoleAssign, access_token: Annotated[str | None, Cookie()]) -> UserRole:
    return None
