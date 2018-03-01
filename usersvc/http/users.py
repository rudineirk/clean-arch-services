import json

from falcon import API, Request, Response

from usersvc.use_case.user import CreateUserRequest, UserUseCases

from .adapters import user_asjson


class UserListApi:
    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    def on_get(self, _, resp: Response):
        users = self.ucs.get_all_users()
        resp.content_type = 'application/json'
        resp.body = json.dumps({
            'users': [user_asjson(user) for user in users],
        })

    def on_post(self, req: Request, resp: Response):
        data = json.load(req.bounded_stream)
        req = CreateUserRequest(
            username=data.get('username'),
            fullname=data.get('fullname'),
            email=data.get('email'),
            password=data.get('password'),
        )
        user = self.ucs.create_user(req)
        if not user:
            resp.status = 401
            resp.body = 'Duplicated data'
            return

        resp.content_type = 'application/json'
        resp.body = json.dumps(user_asjson(user))


class UserApi:
    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    def on_get(self, req: Request, resp: Response, uid: str):
        pass

    def on_put(self, req: Request, resp: Response, uid: str):
        pass

    def on_delete(self, req: Request, resp: Response, uid: str):
        pass


def register(app: API, user_list: UserListApi, user: UserApi):
    app.add_route('/api/users', user_list)
    app.add_route('/api/users/{id}', user)
