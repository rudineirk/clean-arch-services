from http import HTTPStatus as http_status

import pytest
from falcon import testing

from usersvc.http.users import UserApi, UserListApi
from utils.http.backends.falcon import FalconApp

USERS_URL = '/api/users'
USER_ID_URL = '/api/users/{id}'


@pytest.fixture
def user_api(user_ucs):
    api = UserApi(user_ucs)
    return api


@pytest.fixture
def user_list_api(user_ucs):
    api = UserListApi(user_ucs)
    return api


@pytest.fixture
def users_client(user_api, user_list_api):
    app = FalconApp() \
        .add_api(user_list_api) \
        .add_api(user_api) \
        .configure()
    return testing.TestClient(app.falcon)


def test_list_users(users_client):
    resp = users_client.simulate_get(USERS_URL)

    assert resp.status_code == http_status.OK
    assert resp.json == {
        'users': [
            {
                'id': 0,
                'username': 'admin01',
                'fullname': 'Admin',
                'email': 'admin01@company.com',
                'roles': [
                    'users.admin',
                    'shopping.admin',
                ],
            },
            {
                'id': 1,
                'username': 'user01',
                'fullname': 'User',
                'email': 'user01@company.com',
                'roles': [],
            },
        ],
    }


def test_get_user(users_client):
    resp = users_client.simulate_get(USER_ID_URL.format(id=0))
    assert resp.status_code == http_status.OK
    assert resp.json == {
        'id': 0,
        'username': 'admin01',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': [
            'users.admin',
            'shopping.admin',
        ],
    }


def test_get_user_not_found(users_client):
    resp = users_client.simulate_get(USER_ID_URL.format(id=1000))
    assert resp.status_code == http_status.NOT_FOUND


def test_create_user(users_client):
    resp = users_client.simulate_post(USERS_URL, json={
        'username': 'admin01',
        'password': 'admin123',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    })
    assert resp.status_code == http_status.OK
    assert resp.json == {
        'id': 0,
        'username': 'admin01',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    }


def test_create_user_duplicated(users_client):
    resp = users_client.simulate_post(USERS_URL, json={
        'username': 'test01',
        'password': 'test123',
        'fullname': 'Test',
        'email': 'test01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    })
    assert resp.status_code == http_status.CONFLICT
    assert resp.text == 'Duplicated data'


def test_update_user(users_client):
    resp = users_client.simulate_put(USER_ID_URL.format(id=0), json={
        'username': 'admin01',
        'password': 'admin123',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    })
    assert resp.status_code == http_status.OK
    assert resp.json == {
        'id': 0,
        'username': 'admin01',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    }


def test_update_user_not_found(users_client):
    resp = users_client.simulate_put(USER_ID_URL.format(id=1000), json={
        'username': 'admin01',
        'password': 'admin123',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': ['users.admin', 'shopping.admin'],
    })
    assert resp.status_code == http_status.NOT_FOUND
    assert resp.text == 'User not found'


def test_delete_user(users_client):
    resp = users_client.simulate_delete(USER_ID_URL.format(id=1))
    assert resp.status_code == http_status.OK


def test_delete_user_not_found(users_client):
    resp = users_client.simulate_delete(USER_ID_URL.format(id=1000))
    assert resp.status_code == http_status.NOT_FOUND
