from simple_amqp_rpc import Service
from usersvc.use_cases.user import UserUseCases

from .adapters import user_asjson


class UserService:
    svc = Service('auth.users')

    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    @svc.rpc('ListUsers')
    def list_users(self, req):
        users = self.ucs.get_all_users()
        return {
            'users': [user_asjson(user) for user in users],
        }
