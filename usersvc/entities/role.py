from abc import ABC
from typing import List

from dataclasses import dataclass


@dataclass
class Role:
    name: str
    permissions: List[str]
    id: int = -1


class RolesRepo(ABC):
    def get_role_by_id(self, uid: int) -> Role:
        raise NotImplementedError

    def get_role_by_name(self, name: str) -> Role:
        raise NotImplementedError

    def get_all_roles(self) -> List[Role]:
        raise NotImplementedError

    def create_role(self, role: Role) -> Role:
        raise NotImplementedError

    def update_role(self, role: Role) -> bool:
        raise NotImplementedError

    def delete_role(self, role: Role) -> bool:
        raise NotImplementedError
