from http import HTTPStatus as http_status

from usersvc.use_cases.auth import AuthUseCases, UserLoginRequest
from utils.http import Api, Request, Response, json_response


class AuthApi:
    api = Api('/api/login')

    def __init__(self, ucs: AuthUseCases):
        self.ucs = ucs

    @api.post
    def user_login(self, req: Request):
        try:
            data = req.json
        except ValueError:
            return Response(
                'invalid request body',
                status=http_status.UNSUPPORTED_MEDIA_TYPE,
            )

        missing_fields = []
        if 'username' not in data:
            missing_fields.append('username')
        if 'password' not in data:
            missing_fields.append('password')

        if missing_fields:
            return Response(
                'Missing request fields: '
                + ', '.join(missing_fields),
                status=http_status.BAD_REQUEST,
            )

        req = UserLoginRequest(
            username=data['username'],
            password=data['password'],
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
