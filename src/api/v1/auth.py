from http import HTTPStatus
from typing import Annotated, Dict
from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.responses import Response

from services.auth import get_auth_service
from db.postgres import get_session
from models.schemas import User
from models.users import UserLogin, UserSuccessLogin, UserCreate, UserSuccessRefreshToken
from services.auth import AuthService
from services.jwt import JWTService, get_jwt_service

router = APIRouter()


@router.post('/signup/',
             description="Регистрация пользователя")
async def signup(user_create: UserCreate) -> None:
    return None


@router.post('/login/',
             response_model=UserSuccessLogin,
             description="Аутентификация пользователя")
async def login(user_auth: UserLogin,
                request: Request,
                auth_service: AuthService = Depends(get_auth_service),
                jwt_service: JWTService = Depends(get_jwt_service)) -> UserSuccessLogin:
    user = await auth_service.get_by_login(user_auth.login)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid login or password')
    try:
        await auth_service.check_password(
            user=UserLogin(login=user.login, password=user.password)
        )
        refresh_token = await jwt_service.create_refresh_token(user.id)
        access_token = await jwt_service.create_access_token(user.id)

        await jwt_service.set_refresh_token(refresh_token, user_agent=request.headers.get('User-Agent'))
        await jwt_service.set_access_token(access_token, user.id, user.role_id, 60)

        return UserSuccessLogin(access_token=access_token, refresh_token=refresh_token)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid login or password')


@router.post('/logout/',
             description="Выход пользователя из сессии")
async def logout(full_logout: bool = False, access_token: Annotated[str | None, Cookie()] = None) -> None:
    return None


@router.post('/refresh/',
             description="Обновление токенов")
async def token_refresh(refresh_token: Annotated[str | None, Cookie()] = None) -> UserSuccessRefreshToken:
    return None
