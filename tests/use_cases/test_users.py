import pytest

from usersvc.use_cases.user import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUserByIdRequest,
    UpdateUserRequest,
    UserUseCases
)


@pytest.fixture
def users_ucs(users_repo, roles_repo):
    return UserUseCases(users_repo, roles_repo)


def test_get_all_users(users_ucs):
    users_list = users_ucs.get_all_users()
    users_list = [user.username for user in users_list]
    assert users_list == [
        'admin01',
        'user01',
    ]


def test_get_user_by_id(users_ucs):
    req = GetUserByIdRequest(id=1)
    user = users_ucs.get_user_by_id(req)
    assert user.username == 'user01'


def test_create_user(users_ucs):
    req = CreateUserRequest(
        username='newuser01',
        fullname='New User',
        email='newuser@company.com',
        password='newuser123',
        roles=['users.admin', 'shopping.user'],
    )
    user = users_ucs.create_user(req)
    roles_names = [role.name for role in user.roles]
    assert user.username == req.username
    assert user.fullname == req.fullname
    assert user.email == req.email
    assert user.password == req.password
    assert roles_names == req.roles


def test_create_user_invalid_role(users_ucs):
    req = CreateUserRequest(
        username='newuser01',
        fullname='New User',
        email='newuser@company.com',
        password='newuser123',
        roles=['users.admin', 'invalid.role'],
    )
    resp = users_ucs.create_user(req)
    assert resp == 'invalid role: invalid.role'


def test_update_user(users_ucs, users_repo):
    req = UpdateUserRequest(
        id=0,
        fullname='Updated User',
        email='updated@company.com',
        password='updateduser123',
        roles=['users.admin', 'shopping.user'],
    )
    user = users_ucs.update_user(req)
    roles_names = [role.name for role in user.roles]
    assert user.id == req.id
    assert user.username == 'admin01'
    assert user.fullname == req.fullname
    assert user.email == req.email
    assert user.password == req.password
    assert roles_names == req.roles

    new_user = users_repo.get_user_by_id(0)
    assert new_user.fullname == 'Updated User'


def test_update_user_no_password(users_ucs):
    req = UpdateUserRequest(
        id=0,
        fullname='Updated User',
        email='updated@company.com',
        password='',
        roles=['users.admin', 'shopping.user'],
    )
    user = users_ucs.update_user(req)
    assert user.password == 'admin123'


def test_update_user_not_found(users_ucs):
    req = UpdateUserRequest(
        id=1000,
        fullname='Updated User',
        email='updated@company.com',
        password='updateduser123',
        roles=['users.admin', 'invalid.role'],
    )
    resp = users_ucs.update_user(req)
    assert resp is None


def test_update_user_invalid_role(users_ucs):
    req = UpdateUserRequest(
        id=0,
        fullname='Updated User',
        email='updated@company.com',
        password='updateduser123',
        roles=['users.admin', 'invalid.role'],
    )
    resp = users_ucs.update_user(req)
    assert resp == 'invalid role: invalid.role'


def test_delete_user(users_ucs, users_repo):
    req = DeleteUserRequest(id=0)
    user = users_ucs.delete_user(req)
    assert user.id == 0
    assert user.username == 'admin01'

    resp = users_repo.get_user_by_id(0)
    assert resp is None


def test_delete_user_not_found(users_ucs):
    req = DeleteUserRequest(id=1000)
    user = users_ucs.delete_user(req)
    assert user is None
