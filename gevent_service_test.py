from toolz.functoolz import partial
from typing import NamedTuple


class User(NamedTuple):
    username: str
    password: str
    email: str
    fullname: str
    id: str = None


class Context(NamedTuple):
    ns: str = ''


class Error(NamedTuple):
    code: int
    message: str


class EventsConn:
    def push(self, event, payload):
        pass


def encrypt(password: str) -> str:
    return 'whoosh, encrypted'


def password_strength(password: str) -> int:
    password_length = len(password)
    if password_length < 3:
        return 0
    if password_length < 5:
        return 1
    if password_length < 10:
        return 2

    return 3


def compose(*funcs):
    def compose_pipe(value):
        for func in funcs:
            value, err = func(value)

            if err:
                return value, err

        return value, err

    return compose_pipe


def validate_user_password_strength(user: User) -> (User, Error):
    if password_strength(user.password) > 1:
        return user, None

    return None, Error(400, 'invalid user password')


def encrypt_user_password(user: User, encrypt=encrypt) -> (User, Error):
    user = user._replace(password=encrypt(user.password))
    return user, None


def get_user(user_id: str, coll=None) -> (User, Error):
    user = coll.find_one({'_id': user_id})
    if user is None:
        return None, Error(404, 'user not found')

    return User(
        id=user['_id'],
        username=user['username'],
        password=user['password'],
        email=user['email'],
        fullname=user['fullname'],
    ), None


def create_user(user: User, coll=None) -> (User, Error):
    user_id = coll.insert({
        'username': user.username,
        'password': user.password,
        'email': user.email,
        'fullname': user.fullname,
    }).inserted_id
    if not user_id:
        return None, Error(402, 'duplicated user')

    return user_id, None


def publish_created_user(user: User, events=None) -> (User, Error):
    events.push('created', user)
    return user, None


def create(coll=None, events=None, encrypt=encrypt):
    data_pipe = compose(
        validate_user_password_strength,
        partial(encrypt_user_password, encrypt=encrypt),
        partial(create_user, coll=coll),
        partial(get_user, coll=coll),
        partial(publish_created_user, events=events),
    )

    def create(user: User, ctx) -> (User, Error):
        value, err = data_pipe(user)
        if err:
            return None, err

        return value, None

    return create


async def _create(self, ctx, data, namespace=True):
    self._valid_password_strength(data['password'], [
        data['username'],
        data['email'],
        *data['fullname'].split(),
    ])
    data['password'] = passwords.encrypt(data['password'])
    data['scopes'] = data.get('scopes', [])
    user = await self.coll.create(ctx, data, namespace=namespace)
    await self.publish(ctx, 'created', user)
    return user


def main():
    class MongoResultStub(NamedTuple):
        inserted_id: str = 'doc_id'

    class MongoCollectionStub:
        def __init__(self):
            self.inserted_docs = []
            self.find_queries = []

        def insert(self, doc):
            self.inserted_docs.append(doc)
            return MongoResultStub()

        def find_one(self, query):
            self.find_queries.append(query)
            return {
                '_id': 'doc_id',
                'username': 'teste',
                'password': encrypt('pass'),
                'email': 'email@email.com',
                'fullname': 'teste123',
            }

    class EventsStub:
        def __init__(self):
            self.pushed_events = []

        def push(self, event, payload):
            self.pushed_events.append((event, payload))

    ctx = Context()
    coll = MongoCollectionStub()
    events = EventsStub()
    create_impl = create(coll=coll, events=events, encrypt=encrypt)
    user = User(
        username='teste',
        password='teste123',
        email='email@email.com',
        fullname='teste123',
    )
    resp, err = create_impl(user, ctx)
    assert err is None
    assert resp == User(
        id='doc_id',
        username='teste',
        password='whoosh, encrypted',
        email='email@email.com',
        fullname='teste123',
    )
    assert coll.inserted_docs == [{
        'username': 'teste',
        'password': 'whoosh, encrypted',
        'email': 'email@email.com',
        'fullname': 'teste123',
    }]
    assert coll.find_queries == [{'_id': 'doc_id'}]
    print(resp)


if __name__ == '__main__':
    main()
