from dataclasses import dataclass

from usersvc.entities import Token, User, UsersRepo


@dataclass
class UserLoginRequest:
    username: str
    password: str


@dataclass
class UserHasPermissionRequest:
    user_id: int
    permission: str


def create_user_token(user: User) -> Token:
    token = Token(
        version=1,
        token='insert_token_here',
        permissions=user.permissions,
        owner=user.username,
    )
    return token


class AuthUseCases:
    def __init__(self, repo: UsersRepo):
        self.repo = repo

    def user_login(self, req: UserLoginRequest) -> Token:
        user = self.repo.get_user_by_name(req.username)
        if not user:
            return None

        if user.password != req.password:
            return None

        return create_user_token(user)

    def user_has_permission(self, req: UserHasPermissionRequest) -> bool:
        user = self.repo.get_user_by_id(req.user_id)
        if not user:
            return False

        return req.permission in user.permissions
