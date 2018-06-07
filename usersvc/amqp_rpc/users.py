from simple_amqp_rpc import Service

from usersvc.entities import User
from usersvc.use_cases.user import (
    CreateUserRequest,
    GetUserByIdRequest,
    UserUseCases
)

from .adapters import user_asjson


class UserService:
    svc = Service('auth.users')

    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    @svc.rpc('ListUsers')
    def list_users(self, req):
        users = self.ucs.get_all_users()
        return {
            'ok': True,
            'payload': {
                'users': [user_asjson(user) for user in users],
            },
        }

    @svc.rpc('GetUserById')
    def get_user_by_id(self, req):
        req = GetUserByIdRequest(
            id=req.get('id'),
        )
        user = self.ucs.get_user_by_id(req)
        if not user:
            return {'ok': False, 'error': 'notfound'}

        return user_asjson(user)

    @svc.rpc('CreateUser')
    def create_user(self, req):
        req = CreateUserRequest(
            username=req.get('username'),
            fullname=req.get('fullname'),
            email=req.get('email'),
            password=req.get('password'),
            roles=req.get('roles'),
        )

        user = self.ucs.create_user(req)
        if not isinstance(user, User):
            return {'ok': False, 'error': 'conflict'}

        return {
            'ok': True,
            'payload': user_asjson(user),
        }
