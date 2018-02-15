from typing import List

from dataclasses import dataclass

from .role import Role


@dataclass
class User:
    id: int = -1
    username: str
    fullname: str
    email: str
    password: str
    roles: List[Role]

    def login(self, username: str, password: str) -> bool:
        if username not in [self.username, self.email]:
            return False

        return password == self.password

    def has_permission(self, permission: str) -> bool:
        for role in self.roles:
            if role.has_permission(permission):
                return True

        return False
