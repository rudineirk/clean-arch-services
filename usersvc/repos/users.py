from typing import List

from pymongo import MongoClient

from usersvc.entities import User


class UsersRepo:
    def __init__(self, client: MongoClient):
        self.coll = client.auth.users

    def get_user_by_id(self, id_: int) -> User:
        pass

    def get_user_by_name(self, name: str) -> User:
        pass

    def get_users(self) -> List[User]:
        pass

    def update_user(self, user: User) -> bool:
        pass

    def delete_user(self, user: User) -> bool:
        pass

    def create_user(self, user: User) -> User:
        pass
