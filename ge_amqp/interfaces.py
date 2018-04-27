from typing import Callable, Dict

import ulid
from dataclasses import dataclass

from .actions import (
    BindConsumer,
    BindExchange,
    BindQueue,
    CreateChannel,
    CreateConnection,
    DeclareExchange,
    DeclareQueue
)


def create_name(name):
    if not name:
        name = 'private.{}'.format(str(ulid.new()).lower())

    return name


@dataclass(frozen=True)
class AmqpParameters:
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    vhost: str = '/'


class IAmqpConnection:
    def __init__(self, params: AmqpParameters):
        self.actions = []
        self.add_action(CreateConnection(
            host=params.host,
            port=params.port,
            username=params.username,
            password=params.password,
            vhost=params.vhost,
        ))

        self._channel_number = 1

    def channel(self) -> 'IAmqpChannel':
        number = self._channel_number
        self._channel_number += 1

        self.add_action(CreateChannel(
            number=number,
        ))
        return IAmqpChannel(self, number)

    def add_action(self, action):
        self.actions.append(action)

    def publish(
            self,
            channel: 'IAmqpChannel',
            exchange: str,
            routing_key: str,
            payload: bytes,
            headers: Dict[str, str]=None
    ):
        raise NotImplementedError


class IAmqpChannel:
    def __init__(self, conn, number=-1):
        self.conn = conn
        self.number = number

    def queue(
            self,
            name: str='',
            durable: bool=False,
            exclusive: bool=False,
            auto_delete: bool=False
    ) -> 'IAmqpQueue':
        return IAmqpQueue(
            self.conn, self,
            name=name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
        )

    def exchange(
            self,
            name: str ='',
            type: str='direct',
            durable: bool=False,
            auto_delete: bool=False,
            internal: bool=False,
    ) -> 'IAmqpExchange':
        return IAmqpExchange(
            self.conn, self,
            name=name,
            type=type,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
        )


class IAmqpQueue:
    def __init__(
            self,
            conn: IAmqpConnection,
            channel: IAmqpChannel,
            name: str='',
            durable: bool=False,
            exclusive: bool=False,
            auto_delete: bool=False,
    ):
        self.conn = conn
        self.channel = channel
        self.name = create_name(name)

        self.conn.add_action(DeclareQueue(
            channel=channel.number,
            name=self.name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
        ))

    def bind(self, exchange: 'IAmqpExchange', routing_key: str):
        self.conn.add_action(BindQueue(
            channel=self.channel.number,
            queue=self.name,
            exchange=exchange.name,
            routing_key=routing_key,
        ))
        return self

    def consume(
            self,
            callback: Callable,
            auto_ack: bool=False,
            exclusive: bool=False
    ) -> 'IAmqpConsumer':
        return IAmqpConsumer(
            self.conn, self.channel, self,
            callback=callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
        )


class IAmqpExchange:
    def __init__(
            self,
            conn: IAmqpConnection,
            channel: IAmqpChannel,
            name: str = '',
            type: str = '',
            durable: bool = False,
            auto_delete: bool = False,
            internal: bool = False,
    ):
        self.conn = conn
        self.channel = channel
        self.name = create_name(name)

        self.conn.add_action(DeclareExchange(
            channel=channel.number,
            name=self.name,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
        ))

    def bind(self, exchange: 'IAmqpExchange', routing_key: str):
        self.conn.add_action(BindExchange(
            channel=self.channel.number,
            src_exchange=exchange.name,
            dst_exchange=self.name,
            routing_key=routing_key,
        ))
        return self


class IAmqpConsumer:
    def __init__(
            self,
            conn: IAmqpConnection,
            channel: IAmqpChannel,
            queue: IAmqpQueue,
            callback: Callable,
            auto_ack: bool = False,
            exclusive: bool = False
    ):
        self.conn = conn
        self.channel = channel
        self.tag = 'consumer.{}'.format(str(ulid.new()).lower())

        conn.add_action(BindConsumer(
            channel=channel.number,
            queue=queue.name,
            tag=self.tag,
            callback=callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
        ))

    def cancel(self):
        self.channel.cancel(self.tag)
