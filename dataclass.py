from dataclasses import dataclass as dataclass_decorator, asdict, replace
from collections import Sequence


NoneType = type(None)


def serialize_value(value):
    if type(value) in [str, bytes, int, float, bool, NoneType]:
        return value
    elif isinstance(value, dict):
        new_dict = {}
        for key, dict_value in value.items():
            new_dict[key] = serialize_value(value)

        return new_dict
    elif isinstance(value, Sequence):
        return [serialize_value(v) for v in value]

    return value.serialize()


def serialize_dataclass(obj):
    data = {}
    for key in obj.__dataclass_fields__.keys():
        value = getattr(obj, key)
        data[key] = serialize_value(value)

    return data


class BaseDataClass:
    def replace(self, **kwargs):
        return replace(self, **kwargs)

    def __iter__(self):
        data = asdict(self)
        for key, value in data.items():
            yield key, value

    def serialize(self):
        return serialize_dataclass(self)


def dataclass(_cls, *args, **kwargs):
    kwargs['frozen'] = kwargs.get('frozen', True)

    def wrap(cls):
        cls = cls.__class__(cls.__name__, (cls, BaseDataClass), {})
        return dataclass_decorator(cls, **kwargs)

    if _cls is None:
        return wrap

    return wrap(_cls)


@dataclass
class Data:
    value: int


@dataclass
class User:
    name: str
    email: str
    data: Data
    value: None

user = User('aaa', 'aaa@teste.com', [Data(value=1), Data(value=2)], None)
print(user)
print(dict(user))
print(user.replace(email='ccc@teste.com'))
print(user.serialize())
