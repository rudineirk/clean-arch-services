from dataclasses import dataclass

from usersvc.entities import UsersRepo


@dataclass
class UserLoginRequest:
    username: str
    password: str


@dataclass
class UserHasPermissionRequest:
    user_id: int
    permission: str


class AuthUseCases:
    def __init__(self, repo: UsersRepo):
        self.repo = repo

    def user_login(self, req: UserLoginRequest) -> bool:
        user = self.repo.get_user_by_name(req.username)
        if not user:
            return False

        return user.password == req.password

    def user_has_permission(self, req: UserHasPermissionRequest) -> bool:
        user = self.repo.get_user_by_id(req.user_id)
        return req.permission in user.permissions
