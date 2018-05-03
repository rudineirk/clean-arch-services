import pika
from gevent.events import AsyncResult

from .actions import (
    BindConsumer,
    BindExchange,
    BindQueue,
    CreateChannel,
    CreateConnection,
    DeclareExchange,
    DeclareQueue
)
from .base import AmqpConnection
from .data import AmqpParameters


class GeventAmqpConnection(AmqpConnection):
    def __init__(self, params: AmqpParameters):
        super().__init__(params)
        self._pika_conn = None
        self._pika_channels = []
        self._processor_fut = None

    def configure(self):
        pass

    def start(self, auto_reconnect=True):
        pass

    def stop(self):
        pass

    def action_processor(self):
        for action in self.actions:
            self._processor_fut = AsyncResult()
            if isinstance(action, CreateConnection):
                self.connect(action)

            res = self._processor_fut.get()
            if not res:
                return

    def connect(self, action: CreateConnection):
        self._pika_conn = pika.SelectConnection(
            pika.ConnectionParameters(
                host=action.host,
                port=action.port,
                virtual_host=action.vhost,
                credentials=pika.credentials.PlainCredentials(
                    username=action.username,
                    password=action.password,
                )
            ),
            self.on_connection_open,
            stop_ioloop_on_close=False,
        )
