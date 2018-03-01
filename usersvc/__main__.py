from wsgiref.simple_server import make_server

from falcon import API
from pymongo import MongoClient

from .http.falcon import AuthApi, UserApi, UserListApi
from .repos.mongo import RolesRepoMongo, UsersRepoMongo
from .use_case.auth import AuthUseCases
from .use_case.user import UserUseCases


def create_app():
    client = MongoClient()
    roles_repo = RolesRepoMongo(client)
    users_repo = UsersRepoMongo(client)
    users_repo.roles_repo = roles_repo

    user_ucs = UserUseCases(users_repo, roles_repo)
    auth_ucs = AuthUseCases(users_repo)

    app = API()
    auth_api = AuthApi(app, auth_ucs)
    auth_api.register()
    user_api = UserApi(app, user_ucs)
    user_api.register()
    user_list_api = UserListApi(app, user_ucs)
    user_list_api.register()

    return app


def main(app):
    with make_server('', 3000, app) as httpd:
        httpd.serve_forever()


if __name__ == '__main__':
    main(create_app())
