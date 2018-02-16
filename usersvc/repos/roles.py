from typing import List

from pymongo import MongoClient

from usersvc.entities import Role


class RolesRepo:
    def __init__(self, client: MongoClient):
        self.coll = client.auth.roles

    def get_role_by_id(self, id_: int) -> Role:
        pass

    def get_role_by_name(self, name: str) -> Role:
        pass

    def get_roles(self) -> List[Role]:
        pass

    def update_role(self, role: Role) -> bool:
        pass

    def delete_role(self, role: Role) -> bool:
        pass

    def create_role(self, role: Role) -> Role:
        pass
