import json

from falcon import API, Request, Response

from usersvc.repos import UsersRepo
from usersvc.use_case import user as uc

from .adapters import user_asdict, user_fromdict


class UserListApi:
    def __init__(self, repo: UsersRepo):
        self.repo = repo

    def on_get(self, _, resp: Response):
        users = uc.list_users(repo=self.repo)
        resp.content_type = 'application/json'
        resp.body = json.dumps({
            'users': [user_asdict(user) for user in users],
        })

    def on_post(self, req: Request, resp: Response):
        data = json.load(req.bounded_stream)
        user = user_fromdict(data)
        user = uc.create_user(user, repo=self.repo)
        resp.content_type = 'application/json'
        resp.body = json.dumps(user_fromdict(user))


class UserApi:
    def __init__(self, repo: UsersRepo):
        self.repo = repo

    def on_get(self, req: Request, resp: Response, id: str):
        pass

    def on_put(self, req: Request, resp: Response, id: str):
        pass

    def on_delete(self, req: Request, resp: Response, id: str):
        pass


def register(app: API, user_list: UserListApi, user: UserApi):
    app.add_route('/api/users', user_list)
    app.add_route('/api/users/{id}', user)
