from typing import Callable, Dict

from utils.struct import Struct, field

CONTENT_TYPE_MSGPACK = 'application/msgpack'
ENCODING_UTF8 = 'utf8'


class AmqpParameters(metaclass=Struct):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


class AmqpMsg(metaclass=Struct):
    payload: bytes
    content_type: str = CONTENT_TYPE_MSGPACK
    encoding: str = ENCODING_UTF8
    correlation_id: str = ''
    reply_to: str = ''
    expiration: int = -1
    headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


AmqpConsumerCallback = Callable[[AmqpMsg], None]
