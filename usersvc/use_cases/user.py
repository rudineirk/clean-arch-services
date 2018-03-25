from typing import List

from dataclasses import dataclass

from usersvc.entities import Role, RolesRepo, User, UsersRepo


@dataclass
class CreateUserRequest:
    username: str
    fullname: str
    email: str
    password: str
    roles: List[str]


@dataclass
class UpdateUserRequest:
    id: int
    fullname: str
    email: str
    password: str
    roles: List[str]


@dataclass
class GetUserByIdRequest:
    id: int


@dataclass
class DeleteUserRequest:
    id: int


class UserUseCases:
    def __init__(self, repo: UsersRepo, roles_repo: RolesRepo):
        self.repo = repo
        self.roles_repo = roles_repo

    def get_all_users(self) -> List[User]:
        return self.repo.get_all_users()

    def get_user_by_id(self, req: GetUserByIdRequest) -> User:
        return self.repo.get_user_by_id(req.id)

    def create_user(self, req: CreateUserRequest) -> User:
        roles = self._roles_names_to_roles(req.roles)
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

    def update_user(self, req: UpdateUserRequest) -> User:
        user = self.repo.get_user_by_id(req.id)
        if not user:
            return None

        user.fullname = req.fullname
        user.email = req.email
        if req.password:
            user.password = req.password

        roles = self._roles_names_to_roles(req.roles)
        if isinstance(roles, str):  # is error message
            return roles

        user.roles = roles
        self.repo.update_user(user)
        user = self.repo.get_user_by_id(req.id)
        return user

    def delete_user(self, req: DeleteUserRequest) -> User:
        user = self.repo.get_user_by_id(req.id)
        if not user:
            return None

        self.repo.delete_user(user)
        return user

    def _roles_names_to_roles(self, role_names: List[str]) -> List[Role]:
        roles = self.roles_repo.get_all_roles()
        roles = {role.name: role for role in roles}
        user_roles = []
        for name in role_names:
            role = roles.get(name)
            if role is None:
                return 'invalid role: ' + name

            user_roles.append(role)
        return user_roles
