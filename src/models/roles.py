from pydantic import BaseModel
from models.users import UserProfileResult


class CreateRole(BaseModel):
    name: str
    description: str
    is_subscriber: bool | None
    is_superuser: bool | None
    is_manager: bool | None
    is_admin: bool | None


class RoleInDB(BaseModel):
    id: int
    name: str
    is_subscriber: bool
    is_superuser: bool
    is_manager: bool
    is_admin: bool


class RoleToRepresentation(BaseModel):
    id: int
    name: str
    description: str
    is_subscriber: bool
    is_superuser: bool
    is_manager: bool
    is_admin: bool


class RoleDelete(BaseModel):
    id: int


class RoleChangePermission(BaseModel):
    role_id: int
    name: str | None = None
    description: str | None = None
    is_subscriber: bool | None = None
    is_superuser: bool | None = None
    is_manager: bool | None = None
    is_admin: bool | None = None


class RoleAssign(BaseModel):
    user_id: str
    role_id: int


class UserRole(BaseModel):
    user: UserProfileResult
    role: RoleInDB


class RoleError(BaseModel):
    detail: str | None
