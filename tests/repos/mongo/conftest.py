import pytest
from mongomock import MongoClient


@pytest.fixture
def mongo():
    return MongoClient()
