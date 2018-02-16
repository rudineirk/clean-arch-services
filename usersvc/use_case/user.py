from typing import List

from usersvc.entities import User
from usersvc.repos import UsersRepo


def list_users(repo: UsersRepo = None) -> List[User]:
    return repo.get_users()


def create_user(user: User, repo: UsersRepo = None) -> User:
    return repo.create_user(user)


def user_login(username: str, password: str, repo: UsersRepo = None) -> bool:
    user = repo.get_user_by_name(username)
    return user.login(username, password)


def user_check_permission(
        user_id: int,
        permission: str,
        repo: UsersRepo = None,
) -> bool:
    user = repo.get_user_by_id(user_id)
    return permission in user.permissions
