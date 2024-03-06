import pytest
from starlette import status

from functional.settings import settings


@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED),
    (True, 'testlogin', '123', status.HTTP_400_BAD_REQUEST),
])
@pytest.mark.asyncio
async def test_user_sign_up(aiohttp_client, admin, login, password, expected_status):
    user_data = {
        'username': 'testname',
        'login': login,
        'password': password,
        'email': 'test@example.ru',
        'first_name': 'string',
        'last_name': 'string',
        'birth_day': '2024-02-29',
        'picture': 'string',
    }
    url = f'{settings.fastapi.url()}/signup/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        response_status = response.status
    assert response_status == expected_status


@pytest.mark.parametrize('admin, login, password, expected_status, expected_body', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED, {"message": "Login success"}),
    (True, 'testlogin', 't', status.HTTP_400_BAD_REQUEST, {"detail": "Password error"}),
    (True, 'testlogin123', 'testpassword1!S', status.HTTP_400_BAD_REQUEST, {"detail": "User not found"}),
])
@pytest.mark.asyncio
async def test_user_login(aiohttp_client, create_user, admin, login, password, expected_status, expected_body):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        response_status = response.status
        body = await response.json()
    assert response_status == expected_status
    assert body == expected_body


@pytest.mark.parametrize(('admin', 'login', 'password', 'expected_status', 'expected_body'), [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_200_OK, {"message": "Logout success"}),
])
@pytest.mark.asyncio
async def test_user_logout(aiohttp_client, create_user, admin, login, password, expected_status, expected_body):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            access_token_cookie = response.cookies['access_token_cookie'].value
            refresh_token_cookie = response.cookies['refresh_token_cookie'].value
            cookies = {'access_token_cookie': access_token_cookie, 'refresh_token_cookie': refresh_token_cookie}

    url = f'{settings.fastapi.url()}/logout/'

    async with aiohttp_client.delete(url, cookies=cookies, headers=headers) as response:
        body = None
        response_status = response.status
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            body = await response.json()

    assert response_status == expected_status
    assert body == expected_body


@pytest.mark.parametrize(('admin', 'login', 'password', 'expected_status', 'expected_body'), [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED, {"message": "Refresh success"}),
])
@pytest.mark.asyncio
async def test_user_refresh(aiohttp_client, create_user, admin, login, password, expected_status, expected_body):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            access_token_cookie = response.cookies['access_token_cookie'].value
            refresh_token_cookie = response.cookies['refresh_token_cookie'].value
            cookies = {'access_token_cookie': access_token_cookie, 'refresh_token_cookie': refresh_token_cookie}

    url = f'{settings.fastapi.url()}/refresh/'

    async with aiohttp_client.post(url, cookies=cookies, headers=headers) as response:
        body = None
        response_status = response.status
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            body = await response.json()

    assert response_status == expected_status
    assert body == expected_body
