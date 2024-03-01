import pytest
from http import HTTPStatus
from starlette import status

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_user_profile(make_get_request, login_user):
    access_token = login_user['access_token']
    response = await make_get_request({}, "profile/", access_token)
    assert response['status'] == status.HTTP_200_OK
    assert 'username' in response['body']  # Проверьте другие атрибуты профиля


@pytest.mark.asyncio
async def test_change_profile(make_patch_request, login_user):
    access_token = login_user['access_token']
    new_profile_data = {"username": "new_username"}
    response = await make_patch_request(new_profile_data, "profile/", access_token)
    assert response['status'] == status.HTTP_201_CREATED
    assert response['body']['username'] == new_profile_data['username']  # Проверьте другие атрибуты


@pytest.mark.asyncio
async def test_profile_history(make_get_request, login_user):
    access_token = login_user['access_token']
    response = await make_get_request({}, "profile/history", access_token)
    assert response['status'] == status.HTTP_200_OK
    assert isinstance(response['body'], list)  # Проверьте другие атрибуты и тип

@pytest.mark.asyncio

async def test_change_password(make_patch_request, login_user):
    access_token = login_user['access_token']
    new_password_data = {"password": "old_password", "new_password": "new_password"}
    response = await make_patch_request(new_password_data, "profile/change_password/", access_token)
    assert response['status'] == status.HTTP_201_CREATED