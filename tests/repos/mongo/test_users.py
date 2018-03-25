from typing import List
from unittest.mock import patch

import pytest

from usersvc.entities.role import Role, RolesRepo
from usersvc.entities.user import User
from usersvc.repos.mongo.users import UsersRepoMongo

USERS_ADMIN_ROLE = Role(
    id=0,
    name='users.admin',
    permissions=['users:edit', 'users:view'],
)
SHOPPING_ADMIN_ROLE = Role(
    id=1,
    name='shopping.admin',
    permissions=['shopping.list:edit'],
)
SHOPPING_USER_ROLE = Role(
    id=2,
    name='shopping.user',
    permissions=['shopping.list:view'],
)


class RolesRepoStub(RolesRepo):
    def get_all_roles(self) -> List[Role]:
        return [
            USERS_ADMIN_ROLE,
            SHOPPING_ADMIN_ROLE,
            SHOPPING_USER_ROLE,
        ]


@pytest.fixture
def roles_repo_stub():
    return RolesRepoStub()


@pytest.fixture
def users_repo(mongo, roles_repo_stub):
    mongo.auth.drop_collection('users')
    mongo.auth.users.insert_one({
        '_id': 0,
        'username': 'admin01',
        'password': 'admin123',
        'fullname': 'Admin',
        'email': 'admin01@company.com',
        'roles': [0, 1],
    })
    mongo.auth.users.insert_one({
        '_id': 1,
        'username': 'user01',
        'password': 'user123',
        'fullname': 'User',
        'email': 'user01@company.com',
        'roles': [2],
    })
    return UsersRepoMongo(mongo, roles_repo_stub)


def test_get_user_by_id(users_repo):
    user = users_repo.get_user_by_id(0)
    assert user.id == 0
    assert user.username == 'admin01'
    assert user.password == 'admin123'
    assert user.fullname == 'Admin'
    assert user.email == 'admin01@company.com'

    assert len(user.roles) == 2
    assert user.roles[0] == USERS_ADMIN_ROLE
    assert user.roles[1] == SHOPPING_ADMIN_ROLE


def test_get_user_by_id_not_found(users_repo):
    user = users_repo.get_user_by_id(1000)
    assert user is None


def test_get_user_by_name(users_repo):
    user = users_repo.get_user_by_name('admin01')
    assert user.id == 0
    assert user.username == 'admin01'
    assert user.password == 'admin123'
    assert user.fullname == 'Admin'
    assert user.email == 'admin01@company.com'

    assert len(user.roles) == 2
    assert user.roles[0] == USERS_ADMIN_ROLE
    assert user.roles[1] == SHOPPING_ADMIN_ROLE


def test_get_user_by_name_not_found(users_repo):
    user = users_repo.get_user_by_name('invalid_name')
    assert user is None


def test_get_all_users(users_repo):
    users = users_repo.get_all_users()
    assert len(users) == 2
    assert users[0].id == 0
    assert users[0].username == 'admin01'
    assert users[1].id == 1
    assert users[1].username == 'user01'


@patch('usersvc.repos.mongo.users.randint')
def test_create_user(randint_mock, users_repo, mongo):
    randint_mock.return_value = 2

    inserted_id = users_repo.create_user(User(
        username='test_user',
        password='test123',
        fullname='Test',
        email='test@company.com',
        roles=[USERS_ADMIN_ROLE],
    ))
    assert inserted_id == 2

    result = mongo.auth.users.find_one({'_id': 2})
    assert result == {
        '_id': 2,
        'username': 'test_user',
        'password': 'test123',
        'fullname': 'Test',
        'email': 'test@company.com',
        'roles': [0],
    }


def test_update_user(users_repo, mongo):
    resp = users_repo.update_user(User(
        id=0,
        username='updated_user',
        password='updated_pass',
        fullname='Updated',
        email='updated@company.com',
        roles=[SHOPPING_USER_ROLE],
    ))
    assert resp is True

    result = mongo.auth.users.find_one({'_id': 0})
    assert result == {
        '_id': 0,
        'username': 'updated_user',
        'password': 'updated_pass',
        'fullname': 'Updated',
        'email': 'updated@company.com',
        'roles': [2],
    }


def test_update_user_not_found(users_repo):
    resp = users_repo.update_user(User(
        id=1000,
        username='notfound',
        password='',
        fullname='',
        email='',
        roles=[],
    ))
    assert resp is False


def test_delete_user(users_repo, mongo):
    resp = users_repo.delete_user(User(
        id=0,
        username='deleted_user',
        password='',
        fullname='',
        email='',
        roles=[],
    ))
    assert resp is True

    result = mongo.auth.users.find_one({'_id': 0})
    assert result is None

    result = mongo.auth.users.count()
    assert result == 1


def test_delete_user_not_found(users_repo, mongo):
    resp = users_repo.delete_user(User(
        id=1000,
        username='notfound',
        password='',
        fullname='',
        email='',
        roles=[],

    ))
    assert resp is False

    result = mongo.auth.users.count()
    assert result == 2
