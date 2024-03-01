from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status
from starlette.responses import Response

from models.users import ChangeUserProfile, UserProfileResult, UserProfileHistory, UserChangePassword, UserError, \
    Paginator
from services.profile import ProfileInfoService, get_profile_info_service, ProfileHistoryService, \
    get_profile_history_service, ProfileUpdateInfoService, patch_profile_info_service, UpdatePasswordService, \
    update_password_service

router = APIRouter()


@router.get('/profile/',
            description='Информация о пользователе',
            response_model=UserProfileResult,
            responses={status.HTTP_401_UNAUTHORIZED: {'model': UserError},
                       status.HTTP_404_NOT_FOUND: {'model': UserError},
                       status.HTTP_503_SERVICE_UNAVAILABLE: {'model': UserError}})
async def user_profile(user_info: ProfileInfoService = Depends(get_profile_info_service)) -> UserProfileResult:
    answer = await user_info.get_data()
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Ошибка при получении информации о пользователе')


@router.patch('/profile/',
              description='Изменение информации о пользователе',
              status_code=status.HTTP_201_CREATED,
              response_model=UserProfileResult,
              responses={status.HTTP_401_UNAUTHORIZED: {'model': UserError},
                         status.HTTP_404_NOT_FOUND: {'model': UserError},
                         status.HTTP_503_SERVICE_UNAVAILABLE: {'model': UserError}})
async def change_profile(
        user_info: ChangeUserProfile,
        patch_user: ProfileUpdateInfoService = Depends(patch_profile_info_service)
) -> UserProfileResult:
    answer = await patch_user.patch(user_info)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Ошибка при получении информации о пользователе')


@router.get('/profile/history',
            description='История входов пользователя',
            responses={status.HTTP_400_BAD_REQUEST: {'model': UserError},
                       status.HTTP_401_UNAUTHORIZED: {'model': UserError},
                       status.HTTP_404_NOT_FOUND: {'model': UserError},
                       status.HTTP_503_SERVICE_UNAVAILABLE: {'model': UserError}})
async def profile_history(page: Annotated[int, Query(ge=1,
                                          description='Pagination page number')] = 1,
                          limit: Annotated[int, Query(ge=1,
                                           le=100,
                                           description='Pagination page number')] = 10,
                          history: ProfileHistoryService = Depends(get_profile_history_service)
                          ) -> Paginator[UserProfileHistory]:
    answer = await history.get_data(page, limit)
    return answer


@router.patch('/profile/change_password/',
              description='Изменение пароля пользователя',
              status_code=status.HTTP_201_CREATED,
              response_model=None,
              responses={status.HTTP_400_BAD_REQUEST: {'model': UserError},
                         status.HTTP_401_UNAUTHORIZED: {'model': UserError},
                         status.HTTP_404_NOT_FOUND: {'model': UserError},
                         status.HTTP_503_SERVICE_UNAVAILABLE: {'model': UserError}})
async def change_password(passwords: UserChangePassword,
                          password_service: UpdatePasswordService = Depends(update_password_service)) -> Response:
    await password_service.patch(passwords)
    return Response(status_code=status.HTTP_201_CREATED)
