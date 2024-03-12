from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from starlette.responses import Response

from limiter import rate_limit
from services.auth import (get_sign_up_service, SignUpService, LoginService, get_login_service, LogoutService,
                           get_logout_service)
from models.users import UserLogin, UserCreate, UserMessageOut
from services.refresh import RefreshService, get_refresh_service


router = APIRouter()


@router.post('/signup/',
             description="Регистрация пользователя",
             status_code=HTTPStatus.CREATED)
@rate_limit()
async def signup(request: Request,
                 user_create: UserCreate,
                 user_register: SignUpService = Depends(get_sign_up_service)) -> Response:
    user = await user_register.get_data(user_create)
    if user:
        return Response(status_code=HTTPStatus.CREATED)
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Registration error")


@router.post('/login/',
             description="Аутентификация пользователя",
             status_code=HTTPStatus.CREATED,
             response_model=UserMessageOut)
@rate_limit()
async def login(request: Request,
                user_auth: UserLogin,
                user_login: LoginService = Depends(get_login_service),
                user_agent: str = Header("")) -> UserMessageOut:
    await user_login.get_data(user_auth, user_agent)
    return UserMessageOut(message="Login success")


@router.delete('/logout/',
               description="Выход пользователя из сессии",
               status_code=HTTPStatus.OK,
               response_model=UserMessageOut)
async def logout(request: Request,
                 full_logout: bool = False,
                 user_logout: LogoutService = Depends(get_logout_service)) -> UserMessageOut:
    await user_logout.delete(request)
    return UserMessageOut(message="Logout success")


@router.post('/refresh/',
             description="Обновление токенов",
             status_code=HTTPStatus.CREATED,
             response_model=UserMessageOut)
@rate_limit()
async def token_refresh(request: Request,
                        user_token_refresh: RefreshService = Depends(get_refresh_service)) -> UserMessageOut:
    await user_token_refresh.post(request)
    return UserMessageOut(message="Refresh success")
