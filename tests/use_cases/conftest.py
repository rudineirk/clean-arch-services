import pytest

from usersvc.entities.role import Role
from usersvc.entities.user import User, UsersRepo


class UsersRepoStub(UsersRepo):
    def __init__(self):
        self._id_count = 0
        self._data = {}

    def create_user(self, user: User) -> User:
        user.id = self._id_count
        self._id_count += 1
        self._data[user.id] = user

    def get_user_by_name(self, name: str) -> User:
        for item in self._data.values():
            if item.username == name:
                return item

        return None

    def get_user_by_id(self, id: int) -> User:
        try:
            return self._data[id]
        except KeyError:
            pass

        return None


@pytest.fixture
def users_repo():
    repo = UsersRepoStub()

    user = User(
        username='admin01',
        fullname='Admin 01',
        email='admin@company.com',
        password='admin123',
        roles=[
            Role(
                name='users.admin',
                permissions=['users:view', 'users:edit'],
            ),
            Role(
                name='shopping.admin',
                permissions=['shopping.list:edit'],
            ),
        ],
    )
    repo.create_user(user)
    return repo
