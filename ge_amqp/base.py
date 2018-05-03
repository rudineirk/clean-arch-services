from abc import ABCMeta
from typing import Dict

import ulid

from .actions import (
    BindConsumer,
    BindExchange,
    BindQueue,
    CreateChannel,
    CreateConnection,
    DeclareExchange,
    DeclareQueue
)
from .data import AmqpConsumerCallback, AmqpMsg, AmqpParameters


def create_name(name):
    if not name:
        name = 'private.{}'.format(str(ulid.new()).lower())

    return name


class AmqpConnection(metaclass=ABCMeta):
    def __init__(self, params: AmqpParameters):
        self.actions = []
        self.add_action(CreateConnection(
            host=params.host,
            port=params.port,
            username=params.username,
            password=params.password,
            vhost=params.vhost,
        ))

        self._channel_number = 0

    def configure(self):
        raise NotImplementedError

    def start(self, auto_reconnect: bool=True):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def channel(self) -> 'AmqpChannel':
        number = self._channel_number
        self._channel_number += 1

        self.add_action(CreateChannel(
            number=number,
        ))
        return AmqpChannel(self, number)

    def add_action(self, action):
        self.actions.append(action)

    def publish(
            self,
            channel: 'AmqpChannel',
            msg: AmqpMsg,
    ):
        raise NotImplementedError


class AmqpChannel:
    def __init__(self, conn, number=-1):
        self.conn = conn
        self.number = number
        self._queue_cache = {}
        self._exchange_cache = {}

    def queue(
            self,
            name: str='',
            durable: bool=False,
            exclusive: bool=False,
            auto_delete: bool=False,
            props: Dict[str, str]=None,
    ) -> 'AmqpQueue':
        try:
            if name:
                return self._queue_cache[name]
        except KeyError:
            pass

        queue = AmqpQueue(
            self.conn, self,
            name=name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            props=props,
        )
        if not name:
            return queue

        self._queue_cache[name] = queue
        return queue

    def exchange(
            self,
            name: str ='',
            type: str='direct',
            durable: bool=False,
            auto_delete: bool=False,
            internal: bool=False,
            props: Dict[str, str]=None,
    ) -> 'AmqpExchange':
        try:
            if name:
                return self._exchange_cache[name]
        except KeyError:
            pass

        exchange = AmqpExchange(
            self.conn, self,
            name=name,
            type=type,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
            props=props,
        )
        if not name:
            return exchange

        self._exchange_cache[name] = exchange
        return exchange


class AmqpQueue:
    def __init__(
            self,
            conn: AmqpConnection,
            channel: AmqpChannel,
            name: str='',
            durable: bool=False,
            exclusive: bool=False,
            auto_delete: bool=False,
            props: Dict[str, str]=None,
    ):
        self.conn = conn
        self.channel = channel
        self.name = create_name(name)

        if props is None:
            props = {}

        self.conn.add_action(DeclareQueue(
            channel=channel.number,
            name=self.name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            props=props,
        ))

    def bind(self, exchange: 'AmqpExchange', routing_key: str):
        self.conn.add_action(BindQueue(
            channel=self.channel.number,
            queue=self.name,
            exchange=exchange.name,
            routing_key=routing_key,
        ))
        return self

    def consume(
            self,
            callback: AmqpConsumerCallback,
            auto_ack: bool=False,
            exclusive: bool=False
    ) -> 'AmqpConsumer':
        return AmqpConsumer(
            self.conn, self.channel, self,
            callback=callback,
            auto_ack=auto_ack,
            exclusive=exclusive,
        )


class AmqpExchange:
    def __init__(
            self,
            conn: AmqpConnection,
            channel: AmqpChannel,
            name: str = '',
            type: str = '',
            durable: bool = False,
            auto_delete: bool = False,
            internal: bool = False,
            props: Dict[str, str]=None,
    ):
        self.conn = conn
        self.channel = channel
        self.name = create_name(name)

        if props is None:
            props = {}

        self.conn.add_action(DeclareExchange(
            channel=channel.number,
            name=self.name,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
            props=props,
        ))

    def bind(self, exchange: 'AmqpExchange', routing_key: str):
        self.conn.add_action(BindExchange(
            channel=self.channel.number,
            src_exchange=exchange.name,
            dst_exchange=self.name,
            routing_key=routing_key,
        ))
        return self


class AmqpConsumer:
    def __init__(
            self,
            conn: AmqpConnection,
            channel: AmqpChannel,
            queue: AmqpQueue,
            callback: AmqpConsumerCallback,
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
