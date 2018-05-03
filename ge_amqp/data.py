from typing import Callable, Dict

from utils.struct import Struct, field

CONTENT_TYPE_MSGPACK = 'application/msgpack'


class AmqpParameters(metaclass=Struct):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


class AmqpMsg(metaclass=Struct):
    payload: bytes
    content_type: str = CONTENT_TYPE_MSGPACK
    correlation_id: str = ''
    reply_to: str = ''
    headers: Dict[str, str] = field(default_factory=dict)


AmqpConsumerCallback = Callable[[AmqpMsg], None]
