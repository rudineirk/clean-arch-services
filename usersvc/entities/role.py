from typing import List

from dataclasses import dataclass


@dataclass
class Role:
    id: int = -1
    name: str
    permissions: List[str]

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
