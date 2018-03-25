from http import HTTPStatus as http_status

import pytest
from falcon import testing

from usersvc.http.auth import AuthApi
from utils.http.backends.falcon import FalconApp

LOGIN_URL = '/api/login'


@pytest.fixture
def auth_api(auth_ucs):
    api = AuthApi(auth_ucs)
    return api


@pytest.fixture
def auth_client(auth_api):
    app = FalconApp() \
        .add_api(auth_api) \
        .configure()
    return testing.TestClient(app.falcon)


def test_user_login(auth_client):
    resp = auth_client.simulate_post(LOGIN_URL, json={
        'username': 'valid_user',
        'password': 'valid_pass',
    })

    resp.status_code == http_status.OK
    resp.json == {
        'token': 'user_token',
    }


def test_user_login_missing_body(auth_client):
    resp = auth_client.simulate_post(LOGIN_URL)
    assert resp.status_code == http_status.UNSUPPORTED_MEDIA_TYPE


def test_user_login_missing_fields(auth_client):
    resp = auth_client.simulate_post(LOGIN_URL, json={})
    assert resp.status_code == http_status.BAD_REQUEST
    assert resp.text == 'Missing request fields: username, password'


def test_user_login_invalid_user(auth_client):
    resp = auth_client.simulate_post(LOGIN_URL, json={
        'username': 'invalid_user',
        'password': 'invalid_password',
    })
    assert resp.status_code == http_status.NOT_FOUND
    assert resp.text == 'Username or password incorrect'
