from unittest.mock import patch

import pytest

from usersvc.entities.role import Role
from usersvc.repos.mongo.roles import RolesRepoMongo


@pytest.fixture
def roles_repo(mongo):
    mongo.auth.drop_collection('roles')
    mongo.auth.roles.insert_one({
        '_id': 0,
        'name': 'users.admin',
        'permissions': ['users:edit', 'users:view'],
    })
    mongo.auth.roles.insert_one({
        '_id': 1,
        'name': 'shopping.admin',
        'permissions': ['shopping.list:edit'],
    })
    return RolesRepoMongo(mongo)


def test_get_role_by_id(roles_repo):
    role = roles_repo.get_role_by_id(0)
    assert role.id == 0
    assert role.name == 'users.admin'
    assert role.permissions == [
        'users:edit',
        'users:view',
    ]


def test_get_role_by_id_not_found(roles_repo):
    role = roles_repo.get_role_by_id(1000)
    assert role is None


def test_get_role_by_name(roles_repo):
    role = roles_repo.get_role_by_name('users.admin')
    assert role.id == 0
    assert role.name == 'users.admin'
    assert role.permissions == [
        'users:edit',
        'users:view',
    ]


def test_get_role_by_name_not_found(roles_repo):
    role = roles_repo.get_role_by_name('invalid.name')
    assert role is None


def test_get_all_roles(roles_repo):
    roles = roles_repo.get_all_roles()
    assert len(roles) == 2
    assert roles[0].id == 0
    assert roles[0].name == 'users.admin'
    assert roles[1].id == 1
    assert roles[1].name == 'shopping.admin'


@patch('usersvc.repos.mongo.roles.randint')
def test_create_role(randint_mock, roles_repo, mongo):
    randint_mock.return_value = 2

    inserted_id = roles_repo.create_role(Role(
        name='test.role',
        permissions=['test.permission'],
    ))
    assert inserted_id == 2

    result = mongo.auth.roles.find_one({'_id': 2})
    assert result == {
        '_id': 2,
        'name': 'test.role',
        'permissions': ['test.permission'],
    }


def test_update_role(roles_repo, mongo):
    resp = roles_repo.update_role(Role(
        id=0,
        name='updated.role',
        permissions=['updated.permission'],
    ))
    assert resp is True

    result = mongo.auth.roles.find_one({'_id': 0})
    assert result == {
        '_id': 0,
        'name': 'updated.role',
        'permissions': ['updated.permission'],
    }


def test_update_role_not_found(roles_repo):
    resp = roles_repo.update_role(Role(
        id=1000,
        name='notfound.role',
        permissions=['notfound.permission'],
    ))
    assert resp is False


def test_delete_role(roles_repo, mongo):
    resp = roles_repo.delete_role(Role(
        id=0,
        name='deleted.role',
        permissions=['deleted.permission'],
    ))
    assert resp is True

    result = mongo.auth.roles.find_one({'_id': 0})
    assert result is None

    result = mongo.auth.roles.count()
    assert result == 1


def test_delete_role_not_found(roles_repo, mongo):
    resp = roles_repo.delete_role(Role(
        id=1000,
        name='notfound.role',
        permissions=['notfound.permission'],
    ))
    assert resp is False

    result = mongo.auth.roles.count()
    assert result == 2
