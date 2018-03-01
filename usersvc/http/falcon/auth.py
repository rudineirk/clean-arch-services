import json

import falcon
from falcon import API, Request, Response

from usersvc.use_case.auth import AuthUseCases, UserLoginRequest

HTTP_NOT_FOUND = falcon.HTTP_404


class AuthApi:
    def __init__(self, app: API, ucs: AuthUseCases):
        self.app = app
        self.ucs = ucs

    def register(self):
        self.app.add_route('/api/login', self)

    def on_post(self, req: Request, resp: Response):
        data = json.load(req.bounded_stream)
        req = UserLoginRequest(
            username=data.get('username'),
            password=data.get('password'),
        )
        token = self.ucs.user_login(req)
        if not token:
            resp.status = HTTP_NOT_FOUND
            resp.body = 'Username or password incorrect'
            return

        resp.content_type = 'application/json'
        resp.body = json.dumps({
            'token': token.token,
        })
