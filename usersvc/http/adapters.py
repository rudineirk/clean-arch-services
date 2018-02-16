from usersvc.entities import User


def user_asdict(user: User) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'fullname': user.fullname,
        'roles': [role.id for role in user.roles],
    }


def user_fromdict(data: dict) -> User:
    return User(
        username=data.get('username'),
        email=data.get('email'),
        fullname=data.get('fullname'),
        password=data.get('password'),
        roles=data.get('roles'),
    )
