from typing import Callable, Dict

from utils.struct import Struct, field

CONTENT_TYPE_TEXT_PLAIN = 'text/plain'
ENCODING_UTF8 = 'utf8'


class AmqpParameters(metaclass=Struct):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


class AmqpMsg(metaclass=Struct):
    payload: bytes
    exchange: str = ''
    topic: str = ''
    correlation_id: str = ''
    content_type: str = CONTENT_TYPE_TEXT_PLAIN
    encoding: str = ENCODING_UTF8
    reply_to: str = None
    expiration: int = None
    headers: Dict[str, str] = field(default_factory=dict)


AmqpConsumerCallback = Callable[[AmqpMsg], None]
