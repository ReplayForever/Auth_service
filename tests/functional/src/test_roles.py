import pytest
from sqlalchemy import text

from starlette import status


pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_200_OK),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_403_FORBIDDEN),
])
async def test_get_roles(create_user, login_user, make_get_request, admin, login, password, expected_status):
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value
    response = await make_get_request({}, 'roles/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert isinstance(response['body'], list)


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_200_OK),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_403_FORBIDDEN),
])
async def test_create_role(create_user, async_session, make_post_request, login_user,
                           admin, login, password, expected_status):
    role_data = {
        'name': 'Test Role',
        'description': 'Test Description',
        'is_subscriber': False,
        'is_superuser': False,
        'is_manager': False,
        'is_admin': True,
    }
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value
    response = await make_post_request(role_data, 'roles/', access_token)

    async with async_session() as session:
        async with session.begin():
            await session.execute(
                text('''
                DELETE FROM roles WHERE name = :name;
                '''),
                {'name': role_data['name']}
            )
        await session.commit()

    assert response['status'] == expected_status
    if admin:
        assert 'id' in response['body']
        assert response['body']['name'] == role_data['name']


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_200_OK),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_403_FORBIDDEN),
])
async def test_delete_role(create_user, make_delete_request, create_role, login_user,
                           admin, login, password, expected_status):
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value
    role_id = create_role
    response = await make_delete_request({'id': role_id}, 'roles/', access_token)
    assert response['status'] == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_200_OK),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_403_FORBIDDEN),
])
async def test_update_role(create_user, make_patch_request, create_role, login_user,
                           admin, login, password, expected_status):
    role_id = create_role
    role_data = {
        'role_id': role_id,
        'name': 'Updated Role',
        'is_subscriber': True,
        'is_superuser': True,
        'is_manager': True,
        'is_admin': True,
    }
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value
    response = await make_patch_request(role_data, 'roles/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert response['body']['id'] == role_id
        assert response['body']['name'] == role_data['name']


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_200_OK),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_200_OK),
])
async def test_get_user_role(async_session, make_get_request, login_user, create_user,
                             admin, login, password, expected_status):
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value
    async with async_session() as session:
        async with session.begin():
            user_id = await session.execute(text("SELECT id FROM users WHERE login = :login"), {"login": login})
            user_id = str(user_id.scalar())

    response = await make_get_request({'user_id': user_id}, f'user_role/{user_id}/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert 'id' in response['body']


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, login, password, expected_status', [
    (True, 'testloginTrue', 'testpassword1!S', status.HTTP_201_CREATED),
    (False, 'testloginFalse', 'testpassword1!S', status.HTTP_403_FORBIDDEN),
])
async def test_assign_role(create_role, create_user, make_post_request, login_user,
                           admin, login, password, expected_status):
    tokens = await login_user(login, password)
    access_token = tokens['access_token_cookie'].value

    user_id = create_user
    role_id = create_role

    role_assign_data = {
        'user_id': user_id,
        'role_id': role_id,
    }
    response = await make_post_request(role_assign_data, 'user_role/', access_token)
    assert response['status'] == expected_status
    if admin:
        assert 'role' in response['body']
        assert 'user' in response['body']
        assert response['body']['role']['id'] == role_id
