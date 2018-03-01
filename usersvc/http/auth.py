import json
from http import HTTPStatus

from falcon import API, Request, Response

from usersvc.use_case.auth import AuthUseCases, UserLoginRequest


class AuthApi:
    def __init__(self, ucs: AuthUseCases):
        self.ucs = ucs

    def on_post(self, req: Request, resp: Response):
        data = json.load(req.bounded_stream)
        req = UserLoginRequest(
            username=data.get('username'),
            password=data.get('password'),
        )
        token = self.ucs.user_login(req)
        if not token:
            resp.status = HTTPStatus.NOT_FOUND
            resp.body = 'Username or password incorrect'
            return

        resp.content_type = 'application/json'
        resp.body = json.dumps({
            'token': token.token,
        })


def register(app: API, auth: AuthApi):
    app.add_route('/api/login', auth)
