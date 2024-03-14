from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.responses import Response

from limiter import rate_limit
from models.users import ChangeUserProfile, UserProfileResult, UserProfileHistory, UserChangePassword, UserError, \
    Paginator
from services.profile import ProfileInfoService, get_profile_info_service, ProfileHistoryService, \
    get_profile_history_service, ProfileUpdateInfoService, patch_profile_info_service, UpdatePasswordService, \
    update_password_service

router = APIRouter()


@router.get('/profile/',
            description='Информация о пользователе',
            response_model=UserProfileResult,
            responses={HTTPStatus.UNAUTHORIZED: {'model': UserError},
                       HTTPStatus.NOT_FOUND: {'model': UserError},
                       HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
@rate_limit()
async def user_profile(request: Request,
                       user_info: ProfileInfoService = Depends(get_profile_info_service)) -> UserProfileResult:
    answer = await user_info.get_data()
    if answer:
        return answer
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Error while retrieving user information')


@router.patch('/profile/',
              description='Изменение информации о пользователе',
              status_code=HTTPStatus.CREATED,
              response_model=UserProfileResult,
              responses={HTTPStatus.UNAUTHORIZED: {'model': UserError},
                         HTTPStatus.NOT_FOUND: {'model': UserError},
                         HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
@rate_limit()
async def change_profile(
        request: Request,
        user_info: ChangeUserProfile,
        patch_user: ProfileUpdateInfoService = Depends(patch_profile_info_service)
) -> UserProfileResult:
    answer = await patch_user.patch(user_info)
    if answer:
        return answer
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Error while retrieving user information')


@router.get('/profile/history',
            description='История входов пользователя',
            responses={HTTPStatus.BAD_REQUEST: {'model': UserError},
                       HTTPStatus.UNAUTHORIZED: {'model': UserError},
                       HTTPStatus.NOT_FOUND: {'model': UserError},
                       HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
@rate_limit()
async def profile_history(request: Request,
                          page: Annotated[int, Query(ge=1,
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
              status_code=HTTPStatus.CREATED,
              response_model=None,
              responses={HTTPStatus.BAD_REQUEST: {'model': UserError},
                         HTTPStatus.UNAUTHORIZED: {'model': UserError},
                         HTTPStatus.NOT_FOUND: {'model': UserError},
                         HTTPStatus.SERVICE_UNAVAILABLE: {'model': UserError}})
@rate_limit()
async def change_password(request: Request,
                          passwords: UserChangePassword,
                          password_service: UpdatePasswordService = Depends(update_password_service)) -> Response:
    await password_service.patch(passwords)
    return Response(status_code=HTTPStatus.CREATED)
