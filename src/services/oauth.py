from datetime import datetime
from functools import lru_cache
from http import HTTPStatus

import aiohttp
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.postgres import get_session
from models.schemas import LoginHistory, Role, Token, User, SocialNetwork
from models.users import UserYandexCreate, SocialNetworkCreate
from services.abstract import AbstractService
from utils.helpers import generate_random_password

AUTH_URL = "https://oauth.yandex.ru/authorize"
TOKEN_URL = "https://oauth.yandex.ru/token"
LOGIN_INFO_URL = "https://login.yandex.ru/info"


class YandexAuthServiceLogin(AbstractService):

    async def get_data(self):
        auth_request_url = f"{AUTH_URL}?response_type=code&client_id={settings.yandex.client_id}"
        return RedirectResponse(auth_request_url)


class YandexAuthServiceCallback(AbstractService):
    def __init__(self, db: AsyncSession, authorize: AuthJWT):
        self._db = db
        self._authorize = authorize

    async def get_data(self, code: str, user_agent: str):
        access_token = await self.get_user_token(code)
        if not access_token:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Failed to obtain access token")
        user_info = await self.get_user_info(access_token)

        user_found = await self.get_user_by_yandex_email(user_info['default_email'])
        if not user_found:
            await self.create_user_for_db(user_info)
            user = await self.get_user_by_yandex_email(user_info['default_email'])
            await self.social_network_for_db(user.id)
        else:
            await self.user_update(user_found, user_info)

        await self.authorize_user(user_info, user_agent)
        return {"user_info": user_info}

    @staticmethod
    async def get_user_token(code):

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.yandex.client_id,
            "client_secret": settings.yandex.client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, data=data) as token_response:
                response_data = await token_response.json()

        if "error" in response_data:
            raise HTTPException(status_code=400, detail=response_data['error_description'])

        access_token = response_data["access_token"]

        return access_token

    @staticmethod
    async def get_user_info(access_token: str):
        headers = {'Authorization': 'Bearer ' + access_token}
        url = LOGIN_INFO_URL

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                user_info = await response.json()

        return user_info

    async def create_user_for_db(self, user_info: dict):
        user_data = UserYandexCreate(
            username=user_info['login'],
            login=user_info['login'],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            email=user_info["default_email"],
            birth_day=datetime.strptime(user_info.get('birthday'), "%Y-%m-%d") if user_info.get('birthday') else None,
            password=generate_random_password(),
            picture=None,
            social_network_login=user_info["login"],
            is_verified_email=True
        )
        user = User(**jsonable_encoder(user_data))
        result = await self._db.execute(select(Role).where(
            Role.is_admin == False,
            Role.is_subscriber == False,
            Role.is_superuser == False,
            Role.is_manager == False
        ))
        role = result.fetchone()

        if role is None:
            role = Role(name="Base user",
                        description="Base user role",
                        is_admin=False,
                        is_superuser=False,
                        is_subscriber=False,
                        is_manager=False)
            self._db.add(role)
            await self._db.commit()
            await self._db.refresh(role)

            user.role_id = role.id
            await self.db_add_user(user)
        else:
            user.role_id = role[0].id
            await self.db_add_user(user)

        return user

    async def db_add_user(self, user):
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)

    async def authorize_user(self, user_info: dict, user_agent: str):
        user_found = await self.get_user_by_yandex_email(user_info['default_email'])
        if not user_found:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User not found')

        refresh_token = await self._authorize.create_refresh_token(subject=str(user_found.id))
        access_token = await self._authorize.create_access_token(subject=str(user_found.id),
                                                                 user_claims={'role_id': user_found.role_id})

        await self._authorize.set_access_cookies(access_token)
        await self._authorize.set_refresh_cookies(refresh_token)

        await self.set_by_login_history(user_id=user_found.id, user_agent=user_agent)
        await self.set_refresh_token(user_id=user_found.id, user_agent=user_agent,
                                     refresh_token=refresh_token)

    async def get_user_by_yandex_email(self, email: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()
        return user if user else None

    async def set_by_login_history(self, user_id: str, user_agent: str):
        history = LoginHistory(user_id=user_id, user_agent=user_agent)
        self._db.add(history)
        await self._db.commit()

    async def set_refresh_token(self, user_id: str, user_agent: str, refresh_token: str):
        token = Token(user_id=user_id, user_agent=user_agent, refresh_token=refresh_token)
        self._db.add(token)
        await self._db.commit()

    async def user_update(self, user_found, user_info: dict):
        user_found.social_network_login = user_info['login']
        user_found.first_name = user_info['first_name']
        user_found.last_name = user_info['last_name']
        user_found.is_verified_email = True
        await self.db_add_user(user_found)

    async def social_network_for_db(self, user_id):
        data = SocialNetworkCreate(
            name='Yandex',
            user_id=user_id
        )
        social_network = SocialNetwork(**jsonable_encoder(data))
        self._db.add(social_network)
        await self._db.commit()
        await self._db.refresh(social_network)

@lru_cache()
def get_yandex_login_service() -> YandexAuthServiceLogin:
    return YandexAuthServiceLogin()


@lru_cache()
def get_yandex_callback_service(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends()
) -> YandexAuthServiceCallback:
    return YandexAuthServiceCallback(db, authorize)