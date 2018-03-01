import json

import falcon
from falcon import API, Request, Response

from usersvc.entities import User
from usersvc.use_case.user import (
    CreateUserRequest,
    DeleteUserRequest,
    GetUserByIdRequest,
    UpdateUserRequest,
    UserUseCases
)

from .adapters import user_asjson

HTTP_OK = falcon.HTTP_200
HTTP_NOT_FOUND = falcon.HTTP_404
HTTP_CONFLICT = falcon.HTTP_409


class UserListApi:
    def __init__(self, app: API, ucs: UserUseCases):
        self.app = app
        self.ucs = ucs

    def register(self):
        self.app.add_route('/api/users', self)

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
            roles=data.get('roles'),
        )
        user = self.ucs.create_user(req)
        if not isinstance(user, User):
            resp.status = HTTP_CONFLICT
            resp.body = 'Duplicated data'
            return

        resp.content_type = 'application/json'
        resp.body = json.dumps(user_asjson(user))


class UserApi:
    def __init__(self, app: API, ucs: UserUseCases):
        self.app = app
        self.ucs = ucs

    def register(self):
        self.app.add_route('/api/users/{uid}', self)

    def on_get(self, req: Request, resp: Response, uid: str):
        req = GetUserByIdRequest(id=int(uid))
        user = self.ucs.get_user_by_id(req)
        if not user:
            resp.status = HTTP_NOT_FOUND
            return

        resp.context_type = 'application/json'
        resp.body = json.dumps(user_asjson(user))

    def on_put(self, req: Request, resp: Response, uid: str):
        data = json.load(req.bounded_stream)
        req = UpdateUserRequest(
            id=int(uid),
            fullname=data.get('fullname'),
            email=data.get('email'),
            password=data.get('password'),
            roles=data.get('roles'),
        )
        user = self.ucs.create_user(req)
        if not isinstance(user, User):
            resp.status = HTTP_CONFLICT
            resp.body = 'Duplicated data'
            return

        resp.content_type = 'application/json'
        resp.body = json.dumps(user_asjson(user))

    def on_delete(self, req: Request, resp: Response, uid: str):
        req = DeleteUserRequest(id=int(uid))
        user = self.ucs.delete_user(req)
        if not user:
            resp.status = HTTP_NOT_FOUND
            return
