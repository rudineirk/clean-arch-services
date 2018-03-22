from usersvc.use_cases.user import UserUseCases
from utils.amqp_rpc import Service, mp_response

from .adapters import user_asjson


class UserService:
    svc = Service('auth.Users')

    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    @svc.rpc('ListUsers')
    def list_users(self, req):
        users = self.ucs.get_all_users()
        return mp_response({
            'users': [user_asjson(user) for user in users],
        })
