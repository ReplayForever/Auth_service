from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Header, Request
from starlette.responses import Response

from models.users import UserLogin, UserSuccessLogin, UserCreate, UserSuccessRefreshToken
from services.auth import get_sign_up_service, SignUpService
from services.login import LoginService, get_login_service
from services.logout import LogoutService, get_logout_service

# from services.logout import LogoutService, get_logout_service
# from services.refresh import RefreshService, get_refresh_service

router = APIRouter()


@router.post('/signup/',
             description="Регистрация пользователя",
             status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate, user_register: SignUpService = Depends(get_sign_up_service)) -> Response:
    user = await user_register.get_data(user_create)
    if user:
        return Response(status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка при регистрации пользователя")


@router.post('/login/',
             description="Аутентификация пользователя",
             status_code=status.HTTP_201_CREATED,
             response_model=UserSuccessLogin)
async def login(user_auth: UserLogin,
                user_login: LoginService = Depends(get_login_service),
                user_agent: str = Header("")) -> UserSuccessLogin:
    tokens = await user_login.get_data(user_auth, user_agent)
    if not tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка при логине")
    return tokens


@router.delete('/logout/',
               description="Выход пользователя из сессии",
               status_code=status.HTTP_200_OK)
async def logout(request: Request,
                 full_logout: bool = False,
                 user_logout: LogoutService = Depends(get_logout_service)) -> dict:
    await user_logout.delete(request)
    return {"msg": "Успешный выход из системы"}

#
# @router.post('/refresh/',
#              description="Обновление токенов",
#              status_code=status.HTTP_201_CREATED)
# async def token_refresh(user_token_refresh: RefreshService = Depends(get_refresh_service)):
#     await user_token_refresh.post()
#     return {"msg": "Токены были изменены"}
