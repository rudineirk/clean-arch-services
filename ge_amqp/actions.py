from typing import Callable

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateConnection:
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


@dataclass(frozen=True)
class CreateChannel:
    number: int = -1


@dataclass(frozen=True)
class DeclareQueue:
    channel: int = -1
    name: str = ''
    durable: bool = False
    exclusive: bool = False
    auto_delete: bool = False


@dataclass(frozen=True)
class DeclareExchange:
    channel: int = -1
    name: str = ''
    type: str = ''
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False


@dataclass(frozen=True)
class BindQueue:
    channel: int = -1
    queue: str = ''
    exchange: str = ''
    routing_key: str = ''


@dataclass(frozen=True)
class BindExchange:
    channel: int = -1
    src_exchange: str = ''
    dst_exchange: str = ''
    routing_key: str = ''


@dataclass(frozen=True)
class BindConsumer:
    channel: int = -1
    queue: str = ''
    tag: str = ''
    callback: Callable = None
    auto_ack: bool = False
    exclusive: bool = False
