from http import HTTPStatus

from fastapi import APIRouter, Depends, Header, HTTPException
from starlette.responses import Response

from services.oauth import (YandexAuthServiceCallback, YandexAuthServiceLogin,
                            get_yandex_callback_service,
                            get_yandex_login_service)

router = APIRouter()


@router.get('/login/yandex',
            description='Логин через Яндекс',
            status_code=HTTPStatus.OK,
            tags=['oauth'])
async def yandex_login(yandex_user: YandexAuthServiceLogin = Depends(get_yandex_login_service)):
    await yandex_user.get_data()


@router.get('/login/yandex/callback',
            description='Функционал работы с пользователем',
            status_code=HTTPStatus.OK,
            tags=['oauth'])
async def yandex_callback(code: str,
                          user_agent: str = Header(""),
                          user_data: YandexAuthServiceCallback = Depends(get_yandex_callback_service)):
    response = await user_data.get_data(code, user_agent)
    if response:
        return Response(status_code=HTTPStatus.OK)
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Login error')

