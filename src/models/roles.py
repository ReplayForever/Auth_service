from pydantic import BaseModel
from models.users import UserProfileResult


class CreateRole(BaseModel):
    name: str
    description: str


class RoleInDB(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RoleDelete(BaseModel):
    id: int


class RoleChangePermission(BaseModel):
    role_id: int
    name: str


class RoleAssign(BaseModel):
    user_id: str
    role_id: int


class UserRole(BaseModel):
    user: UserProfileResult
    role: RoleInDB
    