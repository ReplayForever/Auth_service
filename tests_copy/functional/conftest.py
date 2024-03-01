import asyncio
import random
import uuid
from time import sleep

import aiohttp
import pytest
import redis
from http import HTTPStatus
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests_copy.functional.settings import settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def aiohttp_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()


@pytest.fixture(scope='session')
def make_get_request(aiohttp_client):
    async def inner(params: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        # headers = {}
        cookies = {}
        if access_token:
            cookies['access_token'] = access_token
        async with aiohttp_client.get(url, params=params, cookies=cookies) as response:
            body = await response.json()
            status = response.status
            return {
                'body': body,
                'status': status
            }

    return inner


@pytest.fixture(scope='session')
def make_post_request(aiohttp_client):
    async def inner(body: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.post(url, json=body, headers=headers) as response:
            body = await response.json()
            status = response.status
            return {
                'body': body,
                'status': status
            }

    return inner

@pytest.fixture(scope='session')
def make_put_request(aiohttp_client):
    async def inner(body: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.put(url, json=body, headers=headers) as response:
            body = await response.json()
            status = response.status
            return {
                'body': body,
                'status': status
            }

    return inner

@pytest.fixture(scope='session')
def make_delete_request(aiohttp_client):
    async def inner(body: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.delete(url, json=body, headers=headers) as response:
            body = await response.json()
            status = response.status
            return {
                'body': body,
                'status': status
            }

    return inner


@pytest.fixture(scope='session')
async def redis_client():
    client = redis.Redis(host=settings.redis.host, port=settings.redis.port)
    yield client
    client.close()


@pytest.fixture
async def create_role(async_session):
    async with async_session as session:
        async with session.begin():
            result = await session.execute(text("INSERT INTO roles (name, description, is_subscriber, is_superuser, is_manager, is_admin) "
                                                "VALUES (:name, :description, :is_subscriber, :is_superuser, :is_manager, :is_admin) "
                                                "RETURNING id"),
                                           {"name": "Test Role",
                                            "description": "Test Role Description",
                                            "is_subscriber": False,
                                            "is_superuser": False,
                                            "is_manager": False,
                                            "is_admin": True})
                                            
            role_id = result.scalar()
            yield role_id

            role_exists = await session.execute(text("SELECT id FROM roles WHERE id = :role_id"), {"role_id": role_id})
            role = role_exists.scalar()
            if role:
                await session.execute(text("DELETE FROM roles WHERE id = :role_id"), {"role_id": role_id})


@pytest.fixture
async def create_user(make_post_request, async_session, admin):
    user_data = {
        "username": "testname",
        "login": "testlogin",
        "password": "testpassword1!S",
        "email": "test@example.com",
        "first_name": "string",
        "last_name": "string",
        "birth_day": "2024-02-29",
        "picture": "string"
    }

    response = await make_post_request(user_data, "signup/")
    assert response['status'] == HTTPStatus.CREATED

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                text("INSERT INTO roles (name, description, is_subscriber, is_superuser, is_manager, is_admin) "
                     "VALUES (:name, :description, :is_subscriber, :is_superuser, :is_manager, :is_admin) "
                     "RETURNING id"),
                {"name": "Test Role",
                 "description": "Test Role Description",
                 "is_subscriber": admin,
                 "is_superuser": admin,
                 "is_manager": admin,
                 "is_admin": admin}
            )

            role_id = result.scalar()

            await session.execute(
                text("UPDATE users SET role_id = :role_id WHERE id = :user_id"),
                {"role_id": role_id, "user_id": response['body']['id']}
            )

    yield user_data

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                text("""
                DELETE FROM users WHERE login = :login
                """),
                {"login": "testlogin"}
            )

            await session.execute(
                text("""
                DELETE FROM roles WHERE id = :role_id
                """),
                {"role_id": role_id}
            )

        await session.commit()


    
@pytest.fixture
async def login_user(make_post_request, create_user, admin):
    created_user_data = create_user(admin=admin)
    user_data = {
        "login": created_user_data["login"],
        "password": created_user_data["password"]
    }

    response = await make_post_request(user_data, "login/")

    return response


@pytest.fixture(scope="session")
async def async_session():
    engine = create_async_engine(settings.postgres.url(), echo=True, future=True)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)
    # async with SessionLocal() as session:
    #     yield session
    yield SessionLocal
    # await engine.dispose()


@pytest.fixture(scope="function")
def sync_engine():
    engine = create_engine(settings.postgres.url(), echo=True)
    return engine
    engine.dispose()


@pytest.fixture(scope="function")
def sync_session(sync_engine):
    SessionLocal = sessionmaker(sync_engine)
    return SessionLocal

@pytest.fixture
def delete_user(sync_session):
    with sync_session() as session:
        session.execute(
            text("DELETE FROM users WHERE login = :login"),
            {"login": "testlogin"}
        )
        session.commit()


# @pytest.fixture
# async def delete_user(async_session):
#     async with async_session() as session:
#         async with session.begin():
#             await session.execute(
#                 text("""
#                 DELETE FROM users WHERE login = :login
#                 """),
#                 {"login": "testlogin"}    
#             )

#             await session.commit()
