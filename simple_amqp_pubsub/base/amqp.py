from abc import ABCMeta

from simple_amqp import AmqpMsg, AmqpParameters
from simple_amqp_pubsub.consts import PUBSUB_EXCHANGE, PUBSUB_QUEUE
from simple_amqp_pubsub.data import Event
from simple_amqp_pubsub.encoding import decode_event, encode_event

from .client import PubSubClient
from .conn import BasePubSub


class BaseAmqpPubSub(BasePubSub, metaclass=ABCMeta):
    CLIENT_CLS = PubSubClient

    def __init__(
            self,
            params: AmqpParameters,
            service: str='service.name',
    ):
        super().__init__()
        self.service = service
        self.conn = self._create_conn(params)

        self._publish_services = set()
        self._listen_channel = None
        self._publish_channel = None

    def _create_conn(self, params: AmqpParameters):
        raise NotImplementedError

    def configure(self):
        self._create_publish()
        self._create_listen()

    def start(self, auto_reconnect: bool=True):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def client(self, service: str) -> PubSubClient:
        self._publish_services.add(service)
        return self.CLIENT_CLS(self, service)

    def push_event(self, event: Event):
        msg = self._encode_event(event)
        msg = msg.replace(
            exchange=PUBSUB_EXCHANGE.format(service=event.service),
            topic=event.event,
        )
        return self._send_event_msg(msg)

    def _send_event_msg(self, msg: AmqpMsg):
        raise NotImplementedError

    def _on_event_message(self, msg: AmqpMsg):
        raise NotImplementedError

    def _decode_event(self, msg: AmqpMsg) -> Event:
        return decode_event(msg)

    def _encode_event(self, event: Event) -> AmqpMsg:
        return encode_event(event)

    def _create_publish(self):
        channel = self.conn.channel()
        for service in self._publish_services:
            exchange = PUBSUB_EXCHANGE.format(service=service)
            channel.exchange(exchange, 'topic', durable=True)

        self._publish_channel = channel

    def _create_listen(self):
        channel = self.conn.channel()

        queue_name = PUBSUB_QUEUE.format(service=self.service)
        queue = channel.queue(queue_name, durable=True)
        for service, events in self._listen_services.items():
            exchange_name = PUBSUB_EXCHANGE.format(service=service)
            exchange = channel \
                .exchange(exchange_name, 'topic', durable=True)

            for event in events:
                queue.bind(exchange, event)

        queue.consume(self._on_event_message)
        self._listen_channel = channel
