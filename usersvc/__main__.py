from wsgiref.simple_server import make_server

from pymongo import MongoClient

from utils.http.backends.falcon import FalconApp

from .http import AuthApi, UserApi, UserListApi
from .repos.mongo import RolesRepoMongo, UsersRepoMongo
from .use_cases.auth import AuthUseCases
from .use_cases.user import UserUseCases


def create_app():
    client = MongoClient()
    roles_repo = RolesRepoMongo(client)
    users_repo = UsersRepoMongo(client)
    users_repo.roles_repo = roles_repo

    user_ucs = UserUseCases(users_repo, roles_repo)
    auth_ucs = AuthUseCases(users_repo)

    app = FalconApp() \
        .add_api(AuthApi(auth_ucs)) \
        .add_api(UserApi(user_ucs)) \
        .add_api(UserListApi(user_ucs))

    app.configure()
    return app


def main(app):
    app.run()


if __name__ == '__main__':
    main(create_app())
