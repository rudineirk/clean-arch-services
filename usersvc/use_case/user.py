from typing import List

from dataclasses import dataclass

from usersvc.entities import Role, RolesRepo, User, UsersRepo


@dataclass
class CreateUserRequest:
    username: str
    fullname: str
    email: str
    password: str
    roles: List[int]


@dataclass
class UpdateUserRequest:
    username: str
    fullname: str
    email: str
    password: str
    roles: List[int]


@dataclass
class GetUserByIdRequest:
    id: int


class UserUseCases:
    def __init__(self, repo: UsersRepo, roles_repo: RolesRepo):
        self.repo = repo
        self.roles_repo = roles_repo

    def get_all_users(self) -> List[User]:
        return self.repo.get_all_users()

    def create_user(self, req: CreateUserRequest) -> User:
        roles = self._roles_ids_to_roles(req.roles)
        if isinstance(roles, str):  # is error message
            return roles

        user = User(
            username=req.username,
            fullname=req.fullname,
            email=req.email,
            password=req.password,
            roles=roles,
        )
        user_id = self.repo.create_user(user)
        return self.repo.get_user_by_id(user_id)

    def _roles_ids_to_roles(self, role_ids: List[int]) -> List[Role]:
        roles = self.roles_repo.get_all_roles()
        roles = {role.id: role for role in roles}
        user_roles = []
        for role_id in role_ids:
            role = roles.get(role_id)
            if role is None:
                return 'invalid role id: ' + str(role_id)

            user_roles.append(role)

        return user_roles
