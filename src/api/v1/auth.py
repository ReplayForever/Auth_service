from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from db.postgres import get_session
from models.schemas import User
from models.users import UserLogin, UserSuccessLogin, UserCreate, UserSuccessRefreshToken
from services.jwt import JWT

router = APIRouter()


@router.post('/signup/',
             description="Регистрация пользователя")
async def signup(user_create: UserCreate) -> None:
    return None


@router.post('/login/',
             description="Аутентификация пользователя")
async def login(user_auth: UserLogin,
                db: Session = Depends(get_session),
                jwt: JWT = Depends(),
                request: Request = None) -> UserSuccessLogin:
    user = await db.execute(User.query.filter(User.login == user_auth.login).first())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь с таким логином не найден')

    if not user.check_password(user_auth.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный пароль')

    access_token = await jwt.create_access_token(user_id=str(user.id))
    refresh_token = await jwt.create_refresh_token(user_id=str(user.id))

    await jwt.set_access_token(token=access_token, user_id=str(user.id), role_id=user.role_id,
                               expires_time=3600)
    await jwt.set_refresh_token(token=refresh_token, user_agent=request.headers.get('User-Agent'))

    return UserSuccessLogin(access_token=access_token, refresh_token=refresh_token)


@router.post('/logout/',
             description="Выход пользователя из сессии")
async def logout(full_logout: bool = False, access_token: Annotated[str | None, Cookie()] = None) -> None:
    return None


@router.post('/refresh/',
             description="Обновление токенов")
async def token_refresh(refresh_token: Annotated[str | None, Cookie()] = None) -> UserSuccessRefreshToken:
    return None
