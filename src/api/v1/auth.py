from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Header
from starlette.responses import Response

from models.users import UserLogin, UserSuccessLogin, UserCreate, UserSuccessRefreshToken
from services.auth import get_sign_up_service, SignUpService
from services.login import LoginService, get_login_service

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
             description="Аутентификация пользователя")
async def login(user_auth: UserLogin,
                user_login: LoginService = Depends(get_login_service),
                user_agent: str = Header("")) -> UserSuccessLogin:
    result = await user_login.get_data(user_auth, user_agent)
    return result


@router.post('/logout/',
             description="Выход пользователя из сессии")
async def logout(full_logout: bool = False, access_token: Annotated[str | None, Cookie()] = None) -> None:
    return None


@router.post('/refresh/',
             description="Обновление токенов")
async def token_refresh(refresh_token: Annotated[str | None, Cookie()] = None) -> UserSuccessRefreshToken:
    return None
