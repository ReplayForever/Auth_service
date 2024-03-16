from datetime import datetime, date
from typing import List, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel


T = TypeVar('T')


class UserCreate(BaseModel):
    username: str
    login: str
    password: str
    first_name: str | None
    last_name: str | None
    email: str
    birth_day: date | None
    picture: str | None


class UserYandexCreate(BaseModel):
    username: str
    login: str
    password: str
    first_name: str | None
    last_name: str | None
    email: str
    birth_day: date | None
    picture: str | None
    social_network_login: str
    is_verified_email: bool


class SocialNetworkCreate(BaseModel):
    name: str
    user_id: UUID

class UserInDB(BaseModel):
    id: UUID

    class Config:
        from_attributes = True


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
    username: str | None
    login: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    birth_day: date | None
    role_id: str | int | None
    picture: str | None


class UserChangePassword(BaseModel):
    password: str
    new_password: str


class UserProfileHistory(BaseModel):
    user_agent: str | None = None
    auth_date: datetime


class ChangeUserProfile(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    birth_day: date | None = None
    picture: str | None = None


class UserError(BaseModel):
    detail: str | None


class Paginator(BaseModel, Generic[T]):
    page: int
    limit: int
    results: List[T]


class UserMessageOut(BaseModel):
    message: str = ''