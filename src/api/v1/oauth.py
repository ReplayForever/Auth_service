from http import HTTPStatus

from fastapi import APIRouter, Depends, Header, HTTPException
from starlette.responses import Response

from services.oauth import (YandexAuthServiceCallback, YandexAuthServiceLogin,
                            get_yandex_callback_service,
                            get_yandex_login_service)

router = APIRouter()

YANDEX = 'yandex'


@router.get('/login/social_network/{provider}',
            description='Логин через соц.сеть',
            status_code=HTTPStatus.OK,
            tags=['oauth'])
async def social_network_login(
        provider: str,
        yandex_user: YandexAuthServiceLogin = Depends(get_yandex_login_service)):
    if provider.lower() == YANDEX:
        await yandex_user.get_data()
    else:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='Invalid provider')


@router.get('/login/callback',
            description='Функционал работы с пользователем',
            status_code=HTTPStatus.OK,
            tags=['oauth'])
async def social_network_callback(code: str,
                                  user_agent: str = Header(""),
                                  user_data: YandexAuthServiceCallback = Depends(get_yandex_callback_service)):
    result = await user_data.get_data(code, user_agent)
    if not result:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Login error')
    return result


