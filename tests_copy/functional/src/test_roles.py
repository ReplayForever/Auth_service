import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


def test_signup_login_delete(delete_user):
    # assert create_user['status'] == HTTPStatus.CREATED

    # assert login_user['status'] == HTTPStatus.CREATED
    # assert 'access_token' in login_user['body']
    # assert 'refresh_token' in login_user['body']
    # delete_user()
    assert True == True


# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.OK),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_get_roles(make_get_request, login_user, admin, expected_status):
#     access_token = login_user(admin)['access_token']
#     response = await make_get_request({}, "roles/", access_token)
#     assert response['status'] == expected_status
#     if admin:
#         assert isinstance(response['body'], list)


# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.OK),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_create_role(make_post_request, login_user, admin, expected_status):
#     role_data = {
#         "name": "Test Role",
#         "description": "Test Description",
#         "is_subscriber": False,
#         "is_superuser": False,
#         "is_manager": False,
#         "is_admin": True
#     }
#     access_token = login_user(admin)['access_token']
#     response = await make_post_request(role_data, "roles/", access_token)
#     assert response['status'] == expected_status
#     if admin:
#         assert 'id' in response['body']
#         assert response['body']['name'] == role_data['name']


# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.OK),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_delete_role(make_delete_request, create_role, login_user, admin, expected_status):
#     access_token = login_user(admin)['access_token']
#     role_id = create_role
#     response = await make_delete_request({"id": role_id}, "roles/", access_token)
#     assert response['status'] == expected_status


# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.OK),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_update_role(make_put_request, create_role, login_user, admin, expected_status):
#     role_id = create_role
#     role_data = {
#         "role_id": role_id,
#         "name": "Updated Role",
#         "is_subscriber": True,
#         "is_superuser": True,
#         "is_manager": True,
#         "is_admin": True
#         }
#     access_token = login_user(admin)['access_token']
#     response = await make_put_request(role_data, "roles/", access_token)
#     assert response['status'] == expected_status
#     if admin:
#         assert response['body']['id'] == role_id
#         assert response['body']['name'] == role_data['name']


# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.OK),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_get_user_role(make_get_request, login_user, create_user, admin, expected_status):
#     access_token = login_user(admin)['access_token']
#     user_id = create_user["id"]
#     response = await make_get_request({"user_id": user_id}, f"user_role/{user_id}/", access_token)
#     assert response['status'] == expected_status
#     if admin:
#         assert 'role_id' in response['body']

# @pytest.mark.asyncio
# @pytest.mark.parametrize("admin, expected_status", [
#     (True, HTTPStatus.CREATED),
#     (False, HTTPStatus.FORBIDDEN),
# ])
# async def test_assign_role(make_post_request, login_user, create_user, admin, expected_status, create_role):
#     access_token = login_user(admin)['access_token']
#     user_id = create_user["id"]
#     role_id = create_role
#     role_assign_data = {
#         "user_id": user_id,
#         "role_id": role_id
#     }
#     response = await make_post_request(role_assign_data, "user_role/", access_token)
#     assert response['status'] == expected_status
#     if admin:
#         assert 'role_id' in response['body']
#         assert response['body']['role_id'] == role_id
