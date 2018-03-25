import pytest

from usersvc.use_cases.auth import (
    AuthUseCases,
    UserHasPermissionRequest,
    UserLoginRequest
)


@pytest.fixture
def auth_ucs(users_repo):
    return AuthUseCases(users_repo)


def test_login(auth_ucs):
    req = UserLoginRequest(
        username='admin01',
        password='admin123',
    )
    token = auth_ucs.user_login(req)
    assert token.owner == 'admin01'


def test_login_wrong_password(auth_ucs):
    req = UserLoginRequest(
        username='admin01',
        password='wrong_pass',
    )
    token = auth_ucs.user_login(req)
    assert token is None


def test_login_user_not_found(auth_ucs):
    req = UserLoginRequest(
        username='wrong_user',
        password='admin123',
    )
    token = auth_ucs.user_login(req)
    assert token is None


def test_user_has_permission(auth_ucs):
    req = UserHasPermissionRequest(
        user_id=0,
        permission='users:edit',
    )
    resp = auth_ucs.user_has_permission(req)
    assert resp is True


def test_user_has_permission_no_permission(auth_ucs):
    req = UserHasPermissionRequest(
        user_id=0,
        permission='another.module:edit',
    )
    resp = auth_ucs.user_has_permission(req)
    assert resp is False


def test_user_has_permission_not_found(auth_ucs):
    req = UserHasPermissionRequest(
        user_id=1000,
        permission='users:edit',
    )
    resp = auth_ucs.user_has_permission(req)
    assert resp is False
