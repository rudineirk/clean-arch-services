from http import HTTPStatus as http_status

from usersvc.use_cases.auth import AuthUseCases, UserLoginRequest
from utils.http import Api, Request, Response, json_response


class AuthApi:
    api = Api('/api/login')

    def __init__(self, ucs: AuthUseCases):
        self.ucs = ucs

    @api.post
    def user_login(self, req: Request):
        data = req.json
        req = UserLoginRequest(
            username=data.get('username'),
            password=data.get('password'),
        )
        token = self.ucs.user_login(req)
        if not token:
            return Response(
                'Username or password incorrect',
                status=http_status.NOT_FOUND,
            )

        return json_response({
            'token': token.token,
        })
