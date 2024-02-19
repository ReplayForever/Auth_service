from pydantic import BaseModel


class CreateRole(BaseModel):
    name: str
    description: str


class RoleInDB(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class RoleDelete(BaseModel):
    id: int


class RoleChangePermission(BaseModel):
    role_id: int
    name: str


class RoleAssign(BaseModel):
    user_id: str
    role_id: int
