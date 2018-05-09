import traceback
from time import sleep

import pika
from gevent import spawn
from gevent.event import AsyncResult

from .actions import (
    BindConsumer,
    BindExchange,
    BindQueue,
    CreateChannel,
    CreateConnection,
    DeclareExchange,
    DeclareQueue
)
from .base import AmqpChannel, AmqpConnection, AmqpConsumer
from .data import AmqpMsg, AmqpParameters

NEXT_ACTION = 1


class GeventAmqpConnection(AmqpConnection):
    def __init__(self, params: AmqpParameters):
        super().__init__(params)
        self._pika_conn = None
        self._pika_channels = {}
        self._pika_consumers = {}

        self._closing = False
        self._closing_fut = None
        self._consumer_cancel_fut = None
        self._auto_reconnect = False
        self.reconnect_delay = 1

        self._processor_fut = None
        self._conn_error_handler = None
        self._consumer_error_handler = None

    def add_conn_error_handler(self, handler):
        self._conn_error_handler = handler

    def add_consumer_error_handler(self, handler):
        self._consumer_error_handler = handler

    def configure(self):
        pass

    def start(self, auto_reconnect=True, wait=True):
        self._closing = False
        self._auto_reconnect = auto_reconnect
        if wait:
            self._action_processor()
        else:
            spawn(self._action_processor)

    def stop(self):
        self._closing = True
        self._closing_fut = AsyncResult()

        self._stop_consuming()
        self._close_channels()
        self._closing_fut.get()
        self._closing_fut = None

    def cancel_consumer(self, channel: AmqpChannel, consumer: AmqpConsumer):
        real_channel = self._get_channel(channel.number)
        self._cancel_consumer(real_channel, consumer.tag)

    def publish(self, channel: AmqpChannel, msg: AmqpMsg):
        real_channel = self._get_channel(channel.number)

        properties = pika.BasicProperties(
            content_type=msg.content_type,
            content_encoding=msg.encoding,
            correlation_id=msg.correlation_id,
            reply_to=msg.reply_to,
            expiration=msg.expiration,
            headers=msg.headers,
        )
        real_channel.basic_publish(
            msg.exchange,
            msg.topic,
            msg.payload,
            properties,
        )

    def _action_processor(self):
        while True:
            ok = True
            try:
                self._run_actions()
            except Exception as e:
                self._processor_fut = None
                ok = False
                if self._conn_error_handler:
                    self._conn_error_handler(e)
                else:
                    traceback.print_exc()

            if ok:
                return
            elif not self._auto_reconnect:
                return

            sleep(self.reconnect_delay)

    def _run_actions(self):
        for action in self.actions:
            self._processor_fut = AsyncResult()
            if action.TYPE == CreateConnection.TYPE:
                self._connect(action)
            elif action.TYPE == CreateChannel.TYPE:
                self._create_channel(action)
            elif action.TYPE == DeclareExchange.TYPE:
                self._declare_exchange(action)
            elif action.TYPE == DeclareQueue.TYPE:
                self._declare_queue(action)
            elif action.TYPE == BindExchange.TYPE:
                self._bind_exchange(action)
            elif action.TYPE == BindQueue.TYPE:
                self._bind_queue(action)
            elif action.TYPE == BindConsumer.TYPE:
                self._bind_consumer(action)

            res = self._processor_fut.get()
            if res != NEXT_ACTION:
                break

    def _next_action(self):
        self._processor_fut.set(NEXT_ACTION)

    def _action_error(self, exc):
        self._processor_fut.set_exception(exc)

    def _get_channel(self, number: int):
        return self._pika_channels[number]

    def _set_channel(self, number: int, channel):
        self._pika_channels[number] = channel
        self._pika_consumers[number] = set()

    def _remove_channel(self, number):
        self._pika_channels.pop(number)
        self._pika_consumers.pop(number)

    def _clear_channels(self):
        self._pika_channels = {}
        self._pika_consumers = {}

    def _connect(self, action: CreateConnection):
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
            self._on_connection_open,
            self._on_connection_error,
            self._on_connection_close,
            stop_ioloop_on_close=False,
        )

    def _stop_consuming(self):
        for channel_number, consumer_tags in self._pika_consumers.items():
            channel = self._get_channel(channel_number)
            for consumer_tag in list(consumer_tags):
                self._cancel_consumer(channel, consumer_tag)

    def _cancel_consumer(self, channel, consumer_tag):
        fut = AsyncResult()
        self._consumer_cancel_fut = fut
        channel.basic_cancel(
            consumer_tag=consumer_tag,
            callback=lambda _: fut.set(True),
        )
        fut.get()
        self._consumer_cancel_fut = None
        self._pika_consumers[channel.channel_number].remove(consumer_tag)

    def _close_channels(self):
        for channel in self._pika_channels.values():
            channel.close()

    def _close_connection(self):
        pass

    def _on_connection_open(self, conn):
        self._next_action()

    def _on_connection_error(self, conn, err):
        self._action_error(err)

    def _on_connection_close(self, conn):
        if self._processor_fut:
            self._processor_fut.set_exception(
                ConnectionAbortedError('amqp connection closed'),
            )
            self._processor_fut = None
        if self._consumer_cancel_fut:
            self._consumer_cancel_fut.set_exception(
                ConnectionAbortedError('amqp connection closed'),
            )
            self._consumer_cancel_fut = None

        self._clear_channels()
        if not self._closing and self._auto_reconnect:
            sleep(self.reconnect_delay)
            spawn(self._action_processor)

        self._closing_fut.set(True)

    def _create_channel(self, action: CreateChannel):
        self._pika_conn.channel(self._on_channel_open, action.number)

    def _on_channel_open(self, channel):
        self._set_channel(channel.channel_number, channel)
        channel.add_on_close_callback(self._on_channel_closed)
        self._next_action()

    def _on_channel_closed(self, channel, *_):
        self._remove_channel(channel.channel_number)
        if not self._pika_channels:
            self._pika_conn.close()

    def _declare_queue(self, action: DeclareQueue):
        channel = self._get_channel(action.channel)
        channel.queue_declare(
            queue=action.name,
            durable=action.durable,
            exclusive=action.exclusive,
            auto_delete=action.auto_delete,
            arguments=action.props,
            callback=self._on_queue_declare,
        )

    def _on_queue_declare(self, _):
        self._next_action()

    def _declare_exchange(self, action: DeclareExchange):
        channel = self._get_channel(action.channel)
        channel.exchange_declare(
            exchange=action.name,
            exchange_type=action.type,
            durable=action.durable,
            auto_delete=action.auto_delete,
            internal=action.internal,
            arguments=action.props,
            callback=self._on_exchange_declare,
        )

    def _on_exchange_declare(self, _):
        self._next_action()

    def _bind_queue(self, action: BindQueue):
        channel = self._get_channel(action.channel)
        channel.queue_bind(
            queue=action.queue,
            exchange=action.exchange,
            routing_key=action.routing_key,
            arguments=action.props,
            callback=self._on_bind_queue,
        )

    def _on_bind_queue(self, _):
        self._next_action()

    def _bind_exchange(self, action: BindExchange):
        channel = self._get_channel(action.channel)
        channel.exchange_bind(
            source=action.src_exchange,
            destination=action.dst_exchange,
            routing_key=action.routing_key,
            props=action.props,
            callback=self._on_bind_exchange,
        )

    def _on_bind_exchange(self, _):
        self._next_action()

    def _bind_consumer(self, action: BindConsumer):
        channel = self._get_channel(action.channel)
        self._pika_consumers[channel].add(action.tag)
        callback = action.callback
        auto_ack = action.auto_ack
        nack_requeue = action.nack_requeue

        def consumer_callback(channel, deliver, props, payload):
            delivery_tag = deliver.delivery_tag
            msg = AmqpMsg(
                payload=payload,
                content_type=props.content_type,
                encoding=props.encoding,
                exchange=deliver.exchange,
                topic=deliver.routing_key,
                correlation_id=props.correlation_id,
                reply_to=props.reply_to,
                expiration=props.expiration,
                headers=props.headers,
            )

            result = False
            try:
                result = callback(msg)
            except Exception as e:
                result = False
                if self._consumer_error_handler:
                    self._consumer_error_handler(e)
                else:
                    traceback.print_exc()

            if not auto_ack and result:
                channel.basic_ack(delivery_tag)
            elif not auto_ack:
                channel.basic_nack(
                    delivery_tag,
                    requeue=nack_requeue,
                )

        channel.basic_consume(
            queue=action.queue,
            no_ack=not action.auto_ack,
            exclusive=action.exclusive,
            consumer_tag=action.tag,
            arguments=action.props,
            consumer_callback=consumer_callback,
        )
