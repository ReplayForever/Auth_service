import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('admin, expected_status', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
@pytest.mark.asyncio
async def test_user_profile(make_get_request, login_user, admin, expected_status):
    access_token = login_user(admin=admin)['access_token']
    response = await make_get_request({}, 'profile/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert 'username' in response['body']


@pytest.mark.parametrize('admin, expected_status', [
    (True, status.HTTP_201_CREATED),
    (False, status.HTTP_403_FORBIDDEN),
])
@pytest.mark.asyncio
async def test_change_profile(make_patch_request, login_user, admin, expected_status):
    access_token = login_user(admin=admin)['access_token']
    new_profile_data = {'username': 'new_username'}
    response = await make_patch_request(new_profile_data, 'profile/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert response['body']['username'] == new_profile_data['username']


@pytest.mark.parametrize('admin, expected_status', [
    (True, status.HTTP_200_OK),
    (False, status.HTTP_403_FORBIDDEN),
])
@pytest.mark.asyncio
async def test_profile_history(make_get_request, login_user, admin, expected_status):
    access_token = login_user(admin=admin)['access_token']
    response = await make_get_request({}, 'profile/history', access_token)
    assert response['status'] == expected_status
    if admin:
        assert isinstance(response['body'], list)


@pytest.mark.parametrize('admin, expected_status', [
    (True, status.HTTP_201_CREATED),
    (False, status.HTTP_403_FORBIDDEN),
])
@pytest.mark.asyncio
async def test_change_password(make_patch_request, login_user, admin, expected_status):
    access_token = login_user(admin=admin)['access_token']
    new_password_data = {'password': 'old_password', 'new_password': 'new_password'}
    response = await make_patch_request(new_password_data, 'profile/change_password/', access_token)
    assert response['status'] == status.expected_status
