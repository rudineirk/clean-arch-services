from http import HTTPStatus as http_status

from usersvc.entities import User
from usersvc.use_cases.user import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUserByIdRequest,
    UpdateUserRequest,
    UserUseCases
)
from utils.http import Api, Request, Response, json_response

from .adapters import user_asjson


class UserListApi:
    api = Api('/api/users')

    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    @api.get
    def list_users(self, _):
        users = self.ucs.get_all_users()
        return json_response({
            'users': [user_asjson(user) for user in users],
        })

    @api.post
    def create_user(self, req: Request):
        data = req.json
        req = CreateUserRequest(
            username=data.get('username'),
            fullname=data.get('fullname'),
            email=data.get('email'),
            password=data.get('password'),
            roles=data.get('roles'),
        )
        user = self.ucs.create_user(req)
        if not isinstance(user, User):
            return Response('Duplicated data', status=http_status.CONFLICT)

        return json_response(user_asjson(user))


class UserApi:
    api = Api('/api/users/{uid}')

    def __init__(self, ucs: UserUseCases):
        self.ucs = ucs

    @api.get
    def get_user(self, _, uid: str):
        req = GetUserByIdRequest(id=int(uid))
        user = self.ucs.get_user_by_id(req)
        if not user:
            return Response(status=http_status.NOT_FOUND)

        return json_response(user_asjson(user))

    @api.put
    def update_user(self, req: Request, uid: str):
        data = req.json
        req = UpdateUserRequest(
            id=int(uid),
            fullname=data.get('fullname'),
            email=data.get('email'),
            password=data.get('password'),
            roles=data.get('roles'),
        )
        user = self.ucs.update_user(req)
        if not user:
            return Response('User not found', status=http_status.NOT_FOUND)

        return json_response(user_asjson(user))

    @api.delete
    def delete_user(self, _, uid: str):
        req = DeleteUserRequest(id=int(uid))
        user = self.ucs.delete_user(req)
        if not user:
            return Response(status=http_status.NOT_FOUND)

        return Response()
