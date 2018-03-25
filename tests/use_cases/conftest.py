from typing import List

import pytest

from usersvc.entities.role import Role, RolesRepo
from usersvc.entities.user import User, UsersRepo


class UsersRepoStub(UsersRepo):
    def __init__(self):
        self._id_count = 0
        self._data = {}

    def get_user_by_id(self, uid: int) -> User:
        try:
            return self._data[uid]
        except KeyError:
            pass

        return None

    def get_user_by_name(self, name: str) -> User:
        for item in self._data.values():
            if item.username == name:
                return item

        return None

    def get_all_users(self) -> List[User]:
        return self._data.values()

    def create_user(self, user: User) -> int:
        user.id = self._id_count
        self._id_count += 1
        self._data[user.id] = user

        return user.id

    def update_user(self, user: User) -> User:
        if user.id not in self._data:
            return False

        self._data[user.id] = user
        return True

    def delete_user(self, user: User) -> User:
        if user.id not in self._data:
            return False

        del self._data[user.id]
        return True


class RolesRepoStub(RolesRepo):
    def __init__(self):
        self._id_count = 0
        self._data = {}

    def get_role_by_id(self, uid: int) -> Role:
        try:
            return self._data[uid]
        except KeyError:
            pass

        return None

    def get_role_by_name(self, name: str) -> Role:
        for item in self._data.values():
            if item.name == name:
                return item

        return None

    def get_all_roles(self) -> List[Role]:
        return self._data.values()

    def create_role(self, role: Role) -> int:
        role.id = self._id_count
        self._id_count += 1
        self._data[role.id] = role

        return role.id

    def update_role(self, role: Role) -> Role:
        if role.id not in self._data:
            return False

        self._data[role.id] = role
        return True

    def delete_role(self, role: Role) -> Role:
        if role.id not in self._data:
            return False

        del self._data[role.id]
        return True


@pytest.fixture
def roles_repo():
    repo = RolesRepoStub()
    users_admin_role = Role(
        name='users.admin',
        permissions=['users:view', 'users:edit'],
    )
    shopping_admin_role = Role(
        name='shopping.admin',
        permissions=['shopping.list:edit'],
    )
    shopping_user_role = Role(
        name='shopping.user',
        permissions=['shopping.list:view'],
    )

    repo.create_role(users_admin_role)
    repo.create_role(shopping_admin_role)
    repo.create_role(shopping_user_role)
    return repo


@pytest.fixture
def users_repo(roles_repo):
    repo = UsersRepoStub()

    admin_user = User(
        username='admin01',
        fullname='Admin 01',
        email='admin@company.com',
        password='admin123',
        roles=[
            roles_repo.get_role_by_name('users.admin'),
            roles_repo.get_role_by_name('shopping.admin'),
        ],
    )
    common_user = User(
        username='user01',
        fullname='Common User',
        email='user01@company.com',
        password='user123',
        roles=[
            roles_repo.get_role_by_name('shopping.user'),
        ]
    )
    repo.create_user(admin_user)
    repo.create_user(common_user)
    return repo
