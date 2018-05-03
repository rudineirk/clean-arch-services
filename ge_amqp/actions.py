from typing import Callable, Dict

from utils.struct import Struct, field


class CreateConnection(metaclass=Struct):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


class CreateChannel(metaclass=Struct):
    number: int = -1


class DeclareQueue(metaclass=Struct):
    channel: int = -1
    name: str = ''
    durable: bool = False
    exclusive: bool = False
    auto_delete: bool = False
    props: Dict[str, str] = field(default_factory=dict)


class DeclareExchange(metaclass=Struct):
    channel: int = -1
    name: str = ''
    type: str = ''
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    props: Dict[str, str] = field(default_factory=dict)


class BindQueue(metaclass=Struct):
    channel: int = -1
    queue: str = ''
    exchange: str = ''
    routing_key: str = ''


class BindExchange(metaclass=Struct):
    channel: int = -1
    src_exchange: str = ''
    dst_exchange: str = ''
    routing_key: str = ''


class BindConsumer(metaclass=Struct):
    channel: int = -1
    queue: str = ''
    tag: str = ''
    callback: Callable = None
    auto_ack: bool = False
    exclusive: bool = False
