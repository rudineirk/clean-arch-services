from typing import List

from dataclasses import dataclass


@dataclass
class UserData:
    id: int = -1
    username: str
    fullname: str
    email: str
    password: str
    roles: List[int]


@dataclass
class RoleData:
    id: int = -1
    name: str
    permissions: List[str]


class UserRepository:
    def create_user(self, user: UserData) -> bool:
        raise NotImplementedError

    def update_user(self, user: UserData) -> bool:
        raise NotImplementedError

    def delete_user(self, user_id: int) -> bool:
        raise NotImplementedError

    def get_user(self, user_id: int) -> UserData:
        raise NotImplementedError

    def get_user_by_name(self, username: str) -> UserData:
        raise NotImplementedError


class RoleRepository:
    def create_role(self, role: RoleData) -> bool:
        raise NotImplementedError

    def update_role(self, role: RoleData) -> bool:
        raise NotImplementedError

    def delete_role(self, role: RoleData) -> bool:
        raise NotImplementedError

    def get_role(self, role_id: int) -> RoleData:
        raise NotImplementedError

    def get_role_by_name(self, name: str) -> RoleData:
        raise NotImplementedError
