from typing import Annotated

from fastapi import APIRouter, Cookie

from models.users import ChangeUserProfile, UserProfileResult, UserProfileHistory, UserChangePassword

router = APIRouter()


@router.get('/profile/',
            description="Информация о пользователе")
async def user_profile(access_token: Annotated[str | None, Cookie()] = None) -> UserProfileResult:
    return None


@router.patch('/profile/',
              description="Изменение информации о пользователе")
async def change_profile(access_token: ChangeUserProfile,
                         token: Annotated[str | None, Cookie()] = None) -> UserProfileResult:
    return None


@router.get('/profile/history',
            description="История входов пользователя")
async def profile_history(access_token: Annotated[str | None, Cookie()] = None) -> UserProfileHistory:
    return None


@router.patch('/profile/change_password/',
              description="Изменение пароля пользователя")
async def change_password(password: UserChangePassword, access_token: Annotated[str | None, Cookie()] = None) -> None:
    return None
