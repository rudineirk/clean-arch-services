from typing import List

from usersvc.entities import Role, User


def user_asbson(user: User) -> dict:

    data = {
        'username': user.username,
        'email': user.email,
        'fullname': user.fullname,
        'roles': [role.id for role in user.roles],
    }
    if user.password:
        data['password'] = user.password

    return data


def user_frombson(data: dict, roles: List[Role]) -> User:
    user_roles = []
    for role in roles:
        if role.id in data['roles']:
            user_roles.append(role)

    return User(
        id=data.get('_id'),
        username=data.get('username'),
        email=data.get('email'),
        fullname=data.get('fullname'),
        password=data.get('password'),
        roles=user_roles,
    )


def role_asbson(role: Role) -> dict:
    return {
        'name': role.name,
        'permissions': role.permissions,
    }


def role_frombson(data: dict) -> Role:
    return Role(
        id=data.get('_id'),
        name=data.get('name'),
        permissions=data.get('permissions'),
    )
