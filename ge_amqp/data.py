from typing import Callable, Dict

from dataclasses import dataclass, field

CONTENT_TYPE_MSGPACK = 'application/msgpack'


@dataclass(frozen=True)
class AmqpParameters:
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


@dataclass
class AmqpMsg:
    payload: bytes
    content_type: str = CONTENT_TYPE_MSGPACK
    correlation_id: str = ''
    reply_to: str = ''
    headers: Dict[str, str] = field(default_factory=dict)


AmqpConsumerCallback = Callable[AmqpMsg]
