import hashlib
from datetime import datetime
from random import getrandbits, seed
from unittest.mock import patch

import pytest
from forbiddenfruit import curse, reverse


@pytest.fixture(scope='function', autouse=True)
def patch_os_urandom(request):
    def fake_urandom(s):
        return bytes([getrandbits(8) for _ in range(s)])

    seed(0)
    with patch('os.urandom', fake_urandom):
        yield


@pytest.fixture(scope='session', autouse=True)
def patch_time_module(request):
    with patch('time.time', lambda: 1020304050.123):
        yield


@pytest.fixture(scope='session', autouse=True)
def patch_datetime_now(request):
    date = datetime(2018, 1, 1, 5, 30, 0, 0)
    curse(datetime, 'now', lambda: date)

    def unpatch():
        reverse(datetime, 'now')

    request.addfinalizer(unpatch)


@pytest.fixture(scope='session', autouse=True)
def patch_datetime_utcnow(request):
    date = datetime(2018, 1, 1, 8, 30, 0, 0)
    curse(datetime, 'utcnow', lambda: date)

    def unpatch():
        reverse(datetime, 'utcnow')

    request.addfinalizer(unpatch)


@pytest.fixture(scope='session', autouse=True)
def patch_password_hashing(request):
    def fake_encrypt(password, algorithm=None):
        return '$pbkdf2-sha512$salt123$password-hash'

    def fake_verify(password, password_hash):
        return password_hash == fake_encrypt(password)

    patch_encrypt = patch('libs.passwords.encrypt', fake_encrypt)
    patch_verify = patch('libs.passwords.verify', fake_verify)

    patch_encrypt.__enter__()
    patch_verify.__enter__()

    def unpatch():
        patch_encrypt.__exit__()
        patch_verify.__exit__()

    request.addfinalizer(unpatch)
