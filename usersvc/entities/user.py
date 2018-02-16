from functools import reduce
from typing import List, NamedTuple

from .role import Role


class User(NamedTuple):
    id: int = -1
    username: str
    fullname: str
    email: str
    password: str
    roles: List[Role]

    @property
    def permissions(self) -> List[str]:
        permissions = reduce(
            lambda perms, role: [*perms, *role.permissions],
            self.roles,
            [],
        )
        return list(set(permissions))
