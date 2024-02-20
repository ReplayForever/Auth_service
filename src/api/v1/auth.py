from typing import Annotated

from fastapi import APIRouter, Cookie

from models.users import UserLogin, UserSuccessLogin, UserCreate, UserSuccessRefreshToken

router = APIRouter()


@router.post('/signup/',
             description="Регистрация пользователя")
async def signup(user_create: UserCreate) -> None:
    return None


@router.post('/login/',
             description="Аутентификация пользователя")
async def login(user_auth: UserLogin) -> UserSuccessLogin:
    return None


@router.post('/logout/',
             description="Выход пользователя из сессии")
async def logout(full_logout: bool = False, access_token: Annotated[str | None, Cookie()] = None) -> None:
    return None


@router.post('/refresh/',
             description="Обновление токенов")
async def token_refresh(refresh_token: Annotated[str | None, Cookie()] = None) -> UserSuccessRefreshToken:
    return None
