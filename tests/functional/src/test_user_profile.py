import pytest
from starlette import status

from functional.settings import settings


@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED),
    (True, 'testlogin', 't', status.HTTP_400_BAD_REQUEST),
    (True, 'testlogin123', 'testpassword1!S', status.HTTP_400_BAD_REQUEST),
])
@pytest.mark.asyncio
async def test_user_login(aiohttp_client, create_user, admin, login, password, expected_status):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        response_status = response.status
    assert response_status == expected_status


@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED),
])
@pytest.mark.asyncio
async def test_get_user_profile(aiohttp_client, create_user, admin, login, password, expected_status):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            access_token_cookie = response.cookies['access_token_cookie'].value
            cookies = {'access_token_cookie': access_token_cookie}

    url = f'{settings.fastapi.url()}/profile/'
    async with aiohttp_client.get(url, cookies=cookies, headers=headers) as response:
        body = None
        response_status = response.status
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            body = await response.json()
    user_info = {
        'username': 'testname',
        'login': login,
        'first_name': 'string',
        'last_name': 'string',
        'email': 'test@example.ru',
        'birth_day': '2024-02-29',
        'picture': 'string'}
    body.pop('role_id')
    assert response_status == status.HTTP_200_OK
    assert user_info == body


@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED),
])
@pytest.mark.asyncio
async def test_patch_user_profile(aiohttp_client, create_user, admin, login, password, expected_status):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            access_token_cookie = response.cookies['access_token_cookie'].value
            cookies = {'access_token_cookie': access_token_cookie}

    url = f'{settings.fastapi.url()}/profile/'
    new_user_data = {
        "first_name": "123",
        "last_name": "123",
        "email": "test@test.te",
        "birth_day": "2020-01-01",
        "picture": "path",
    }
    async with aiohttp_client.patch(url, cookies=cookies, headers=headers, json=new_user_data) as response:
        body = None
        response_status = response.status
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            body = await response.json()
    user_info = {
        'username': 'testname',
        'login': login,
        "first_name": "123",
        "last_name": "123",
        "email": "test@test.te",
        "birth_day": "2020-01-01",
        "picture": "path",
    }

    body.pop('role_id')
    assert response_status == status.HTTP_201_CREATED
    assert user_info == body


@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testlogin', 'testpassword1!S', status.HTTP_201_CREATED),
])
@pytest.mark.asyncio
async def test_user_history(aiohttp_client, create_user, admin, login, password, expected_status):
    user_data = {
        'login': login,
        'password': password
    }

    url = f'{settings.fastapi.url()}/login/'
    headers = {}
    async with aiohttp_client.post(url, json=user_data, headers=headers) as response:
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            access_token_cookie = response.cookies['access_token_cookie'].value
            cookies = {'access_token_cookie': access_token_cookie}

    url = f'{settings.fastapi.url()}/profile/history?page=1&limit=10'
    async with aiohttp_client.get(url, cookies=cookies, headers=headers) as response:
        body = None
        response_status = response.status
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            body = await response.json()

    assert response_status == status.HTTP_200_OK
    assert 'page' in body
    assert 'limit' in body
    assert 'results' in body
    assert body['page'] == 1
    assert body['limit'] == 10
