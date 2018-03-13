from usersvc.entities import Role, User


def user_asjson(user: User) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'fullname': user.fullname,
        'roles': [role.id for role in user.roles],
    }


def role_asjson(role: Role) -> dict:
    return {
        'id': role.id,
        'name': role.name,
        'permissions': role.permissions,
    }
