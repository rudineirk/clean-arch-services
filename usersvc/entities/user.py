from abc import ABC
from typing import List

from dataclasses import dataclass

from .role import Role


@dataclass
class User:
    username: str
    fullname: str
    email: str
    password: str
    roles: List[Role]
    id: int = -1

    @property
    def permissions(self) -> List[str]:
        permissions = []
        for role in self.roles:
            permissions.extend(role.permissions)
        return list(set(permissions))


class UsersRepo(ABC):
    def get_user_by_id(self, uid: int) -> User:
        raise NotImplementedError

    def get_user_by_name(self, name: str) -> User:
        raise NotImplementedError

    def get_all_users(self) -> List[User]:
        raise NotImplementedError

    def create_user(self, user: User) -> int:
        raise NotImplementedError

    def update_user(self, user: User) -> bool:
        raise NotImplementedError

    def delete_user(self, user: User) -> bool:
        raise NotImplementedError
