from random import randint
from typing import List

from pymongo import MongoClient

from usersvc.entities import Role, RolesRepo

from .adapters import role_asbson, role_frombson


class RolesRepoMongo(RolesRepo):
    def __init__(self, client: MongoClient):
        self.coll = client.auth.roles

    def get_role_by_id(self, uid: int) -> Role:
        data = self.coll.find_one({'_id': uid})
        if data is None:
            return None

        return role_frombson(data)

    def get_role_by_name(self, name: str) -> Role:
        data = self.coll.find_one({'name': name})
        if data is None:
            return None

        return role_frombson(data)

    def get_all_roles(self) -> List[Role]:
        data = self.coll.find()
        return [role_frombson(role) for role in data]

    def create_role(self, role: Role) -> int:
        insert_data = role_asbson(role)
        insert_data['_id'] = randint(0, 100000)
        data = self.coll.insert_one(insert_data)
        return data.inserted_id

    def update_role(self, role: Role) -> bool:
        data = self.coll.update_one(
            {
                '_id': role.id
            },
            {'$set': role_asbson(role)},
        )
        return data.matched_count >= 1

    def delete_role(self, role: Role) -> bool:
        data = self.coll.delete_one({
            '_id': role.id,
        })
        return data.deleted_count >= 1
