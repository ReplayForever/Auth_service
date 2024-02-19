from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    login: str
    password: str
    first_name: str | None
    last_name: str | None
    email: str
    birth_day: datetime | None
    picture: str | None


class UserInDB(BaseModel):
    id: UUID

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login: str
    password: str


class UserSuccessLogin(BaseModel):
    access_token: str
    refresh_token: str


class UserRefreshToken(BaseModel):
    refresh_token: str


class UserSuccessRefreshToken(BaseModel):
    access_token: str
    refresh_token: str


class UserLogout(BaseModel):
    user_id: str


class UserProfileResult(BaseModel):
    id: str
    username: str
    login:str
    password: str
    email: str


class UserChangePassword(BaseModel):
    password: str
    new_password: str
    confirm_password: str


class UserProfileHistory(BaseModel):
    user_agent: str
    auth_date: datetime


class ChangeUserProfile(BaseModel):
    username: str | None
    password: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    birth_day: datetime | None
    picture: str | None