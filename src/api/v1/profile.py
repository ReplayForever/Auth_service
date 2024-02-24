from typing import Annotated

from fastapi import APIRouter, Cookie, Depends
from starlette import status

from models.users import ChangeUserProfile, UserProfileResult, UserProfileHistory, UserChangePassword
from services.profile import ProfileInfoService, get_profile_info_service, patch_profile_info_service, \
    ProfileUpdateInfoService, UpdatePasswordService, update_password_service

router = APIRouter()


@router.get('/profile/',
            description="Информация о пользователе")
async def user_profile(access_token: Annotated[str | None, Cookie()] = None,
                       user_info: ProfileInfoService = Depends(get_profile_info_service)) -> UserProfileResult:
    answer = await user_info.get_data(access_token)
    return answer


@router.patch('/profile/',
              description="Изменение информации о пользователе",
              status_code=status.HTTP_201_CREATED)
async def change_profile(
        user_info: ChangeUserProfile,
        access_token: Annotated[str | None, Cookie()] = None,
        patch_user: ProfileUpdateInfoService = Depends(patch_profile_info_service)
) -> UserProfileResult:
    answer = await patch_user.patch(access_token, user_info)
    return answer


@router.get('/profile/history',
            description="История входов пользователя")
async def profile_history(access_token: Annotated[str | None, Cookie()] = None) -> UserProfileHistory:
    return None


@router.patch('/profile/change_password/',
              description="Изменение пароля пользователя",
              status_code=status.HTTP_201_CREATED)
async def change_password(passwords: UserChangePassword,
                          access_token: Annotated[str | None, Cookie()] = None,
                          password_service: UpdatePasswordService = Depends(update_password_service)) -> None:
    await password_service.patch(access_token, passwords)
    return None
