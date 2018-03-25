from random import randint
from typing import List

from pymongo import MongoClient

from usersvc.entities import Role, RolesRepo, User, UsersRepo

from .adapters import user_asbson, user_frombson


class UsersRepoMongo(UsersRepo):
    def __init__(self, client: MongoClient, roles_repo: RolesRepo):
        self.coll = client.auth.users
        self.roles_repo = roles_repo

    def _get_roles(self) -> List[Role]:
        return self.roles_repo.get_all_roles()

    def get_user_by_id(self, uid: int) -> User:
        data = self.coll.find_one({'_id': uid})
        if data is None:
            return None

        roles = self._get_roles()
        return user_frombson(data, roles)

    def get_user_by_name(self, name: str) -> User:
        data = self.coll.find_one({'username': name})
        if data is None:
            return None

        roles = self._get_roles()
        return user_frombson(data, roles)

    def get_all_users(self) -> List[User]:
        data = self.coll.find()
        roles = self._get_roles()
        return [user_frombson(user, roles) for user in data]

    def create_user(self, user: User) -> int:
        insert_data = user_asbson(user)
        insert_data['_id'] = randint(0, 100000)
        data = self.coll.insert_one(insert_data)
        return data.inserted_id

    def update_user(self, user: User) -> bool:
        data = self.coll.update_one(
            {
                '_id': user.id
            },
            {'$set': user_asbson(user)},
        )
        return data.matched_count >= 1

    def delete_user(self, user: User) -> bool:
        data = self.coll.delete_one({
            '_id': user.id,
        })
        return data.deleted_count >= 1
