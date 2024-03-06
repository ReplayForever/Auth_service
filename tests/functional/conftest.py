import asyncio
import aiohttp
import pytest
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from functional.settings import settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def aiohttp_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()


@pytest.fixture(scope='function')
def make_get_request(aiohttp_client):
    async def inner(params: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        cookies = {}
        if access_token:
            cookies['access_token'] = access_token
        async with aiohttp_client.get(url, params=params, cookies=cookies) as response:
            body = None
            status = response.status
            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                body = await response.json()
            return {
                'body': body,
                'status': status,
            }

    return inner


@pytest.fixture(scope='function')
def make_post_request(aiohttp_client):
    async def inner(json: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.post(url, json=json, headers=headers) as response:
            body = None
            status = response.status
            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                body = await response.json()
            return {
                'body': body,
                'status': status,
            }

    return inner


@pytest.fixture(scope='function')
def make_patch_request(aiohttp_client):
    async def inner(json: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.patch(url, json=json, headers=headers) as response:
            body = None
            status = response.status
            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                body = await response.json()
            return {
                'body': body,
                'status': status,
            }

    return inner


@pytest.fixture(scope='function')
def make_delete_request(aiohttp_client):
    async def inner(json: dict, method: str, access_token: str = None):
        url = f'{settings.fastapi.url()}/{method}'
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        async with aiohttp_client.delete(url, json=json, headers=headers) as response:
            body = None
            status = response.status
            if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
                body = await response.json()
            return {
                'body': body,
                'status': status,
            }

    return inner


@pytest.fixture(scope='session')
async def redis_client():
    client = redis.Redis(host=settings.redis.host, port=settings.redis.port)
    yield client
    client.close()


@pytest.fixture
async def create_role(async_session):
    async with async_session() as session:
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


@pytest.fixture(scope='function')
async def create_user(make_post_request, async_session, admin):
    user_data = {
        'username': 'testname',
        'login': 'testlogin',
        'password': 'testpassword1!S',
        'email': 'test@example.ru',
        'first_name': 'string',
        'last_name': 'string',
        'birth_day': '2024-02-29',
        'picture': 'string',
    }

    await make_post_request(user_data, 'signup/')

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                text('INSERT INTO roles (name, description, is_subscriber, is_superuser, is_manager, is_admin) '
                     'VALUES (:name, :description, :is_subscriber, :is_superuser, :is_manager, :is_admin) '
                     'RETURNING id'),
                {'name': 'Test Role',
                 'description': 'Test Role Description',
                 'is_subscriber': admin,
                 'is_superuser': admin,
                 'is_manager': admin,
                 'is_admin': admin}
            )

            role_id = result.scalar()

            await session.execute(
                text("UPDATE users SET role_id = :role_id WHERE username = :user_data"),
                {'role_id': role_id, 'user_data': user_data['username']}
            )

    yield user_data

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                text('''
                DELETE FROM login_histories WHERE user_id IN (SELECT id FROM users WHERE login = 'testlogin');
                '''),
            )
            await session.execute(
                text('''
                DELETE FROM tokens WHERE user_id IN (SELECT id FROM users WHERE login = 'testlogin');
                '''),
            )
            await session.execute(
                text('''
                DELETE FROM users WHERE login = 'testlogin';
                '''),
            )
            await session.execute(
                text('''
                DELETE FROM roles WHERE name = 'Test Role';
                '''),
            )
        await session.commit()


@pytest.fixture
async def login_user(make_post_request, create_user, admin):
    user_data = {
        'login': await create_user(admin=admin)['login'],
        'password': await create_user(admin=admin)['password']
    }

    response = await make_post_request(user_data, 'login/')

    return response


@pytest.fixture(scope='session')
async def async_session():
    engine = create_async_engine(settings.postgres.url(), echo=True, future=True)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)
    yield SessionLocal
    await engine.dispose()


@pytest.fixture(scope='function')
def sync_engine():
    engine = create_engine(settings.postgres.url(), echo=True)
    return engine


@pytest.fixture(scope='function')
def sync_session(sync_engine):
    SessionLocal = sessionmaker(sync_engine)
    return SessionLocal
