from typing import List

import pytest

from usersvc.entities.role import Role
from usersvc.entities.token import Token
from usersvc.entities.user import User
from usersvc.use_cases.auth import UserLoginRequest
from usersvc.use_cases.user import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUserByIdRequest,
    UpdateUserRequest
)


class AuthUseCasesStub:
    def user_login(self, req: UserLoginRequest) -> Token:
        if req.username != 'valid_user':
            return None
        if req.password != 'valid_pass':
            return None

        return Token(
            version=1,
            token='user_token',
            owner='valid_user',
            permissions=[
                'users:edit',
                'users:view',
            ],
        )


class UserUseCasesStub:
    roles = [
        Role(
            id=0,
            name='users.admin',
            permissions=['users:edit', 'users:view'],
        ),
        Role(
            id=1,
            name='shopping.admin',
            permissions=['shopping.list:edit'],
        ),
    ]
    role_names = [role.name for role in roles]
    admin_user = User(
        id=0,
        username='admin01',
        password='admin123',
        fullname='Admin',
        email='admin01@company.com',
        roles=roles,
    )
    common_user = User(
        id=1,
        username='user01',
        password='user123',
        fullname='User',
        email='user01@company.com',
        roles=[],
    )

    def get_all_users(self) -> List[User]:
        return [self.admin_user, self.common_user]

    def get_user_by_id(self, req: GetUserByIdRequest) -> User:
        if req.id >= 2:
            return None

        return self.admin_user

    def create_user(self, req: CreateUserRequest) -> User:
        usernames = [
            self.admin_user.username,
            self.common_user.username,
        ]
        if req.username not in usernames:
            return None

        return self.admin_user

    def update_user(self, req: UpdateUserRequest) -> User:
        if req.id >= 2:
            return None

        return self.admin_user

    def delete_user(self, req: DeleteUserRequest) -> User:
        if req.id >= 2:
            return None

        return self.common_user


@pytest.fixture
def auth_ucs():
    return AuthUseCasesStub()


@pytest.fixture
def user_ucs():
    return UserUseCasesStub()
