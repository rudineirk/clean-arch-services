import ulid
from gevent.event import AsyncResult

from ge_amqp import AmqpMsg, AmqpParameters, PikaGeventAmqpConnection

from .data import RpcCall, RpcResp
from .encoding import (
    decode_rpc_call,
    decode_rpc_resp,
    encode_rpc_call,
    encode_rpc_resp
)

RPC_EXCHANGE = 'rpc.{route}'
RPC_QUEUE = 'rpc.{route}'
REPLY_KEY = 'rpc.reply.{correlation_id}'
RPC_TOPIC = 'rpc'


class AmqpRpc:
    def __init__(
            self,
            params: AmqpParameters,
            route='service.name',
            rpc_callback=None,
            call_timeout=5,
    ):
        self.conn = PikaGeventAmqpConnection(params)
        self.listen_route = route
        self.rpc_callback = rpc_callback
        self._call_timeout = 5

        self._rpc_call_channel = None
        self._publish_routes = set()
        self._response_futures = {}
        self._resp_queue = ''

    def start(self, auto_reconnect=True):
        self.conn.start(auto_reconnect)

    def stop(self):
        self.conn.stop()

    def add_publish_route(self, route):
        self._publish_routes.add(route)
        return self

    def configure(self):
        self._create_publish()
        self._create_listen()
        self._create_resp()

    def _create_publish(self):
        channel = self.conn.channel()
        for route in self._publish_routes:
            exchange = RPC_EXCHANGE.format(route=route)
            channel.exchange(exchange, 'topic', durable=True)

        self._rpc_call_channel = channel

    def _create_listen(self):
        exchange_name = RPC_EXCHANGE.format(route=self.listen_route)
        queue_name = RPC_QUEUE.format(route=self.listen_route)

        channel = self.conn.channel()
        exchange = channel \
            .exchange(exchange_name, 'topic', durable=True)
        channel \
            .queue(queue_name, durable=True) \
            .bind(exchange, RPC_TOPIC) \
            .consume(self.on_listen_message)

    def _create_resp(self):
        channel = self.conn.channel()
        queue = channel.queue(auto_delete=True, exclusive=True)
        queue.consume(
            self.on_resp_message,
            auto_ack=True,
            exclusive=True,
        )
        self._resp_queue = queue.name

    def on_listen_message(self, msg: AmqpMsg):
        pass
        # TODO: Implement valid rpc call handler
        #
        # resp = self.rpc_callback(body, props.content_type)
        # reply_key = REPLY_KEY.format(
        #     correlation_id=props.correlation_id,
        # )
        # resp_properties = BasicProperties(
        #     content_type=resp.content_type,
        #     correlation_id=reply_key,
        # )
        # self.publish_channel.publish(
        #     '',
        #     props.reply_to,
        #     resp.body,
        #     resp_properties,
        # )

    def on_resp_message(self, msg: AmqpMsg):
        pass
        # TODO: Implement valid rpc response handler
        #
        # try:
        #     future = self._response_futures.pop(props.correlation_id)
        # except KeyError:
        #     return

        # resp = RawRpcResp(
        #     body=body,
        #     content_type=props.content_type,
        # )
        # future.set(resp)

    def rpc_call(self, call: RpcCall, timeout=-1) -> RpcResp:
        if timeout == -1:
            timeout = self._call_timeout

        msg = encode_rpc_call(call)

        msg.exchange = RPC_EXCHANGE.format(route=call.route)
        msg.topic = RPC_TOPIC
        msg.reply_to = self._resp_queue

        correlation_id = str(ulid.new())
        msg.correlation_id = correlation_id

        self.conn.publish(self._rpc_call_channel, msg)
        future = AsyncResult()
        key = REPLY_KEY.format(
            correlation_id=correlation_id,
        )
        self._response_futures[key] = future

        return future.get(timeout=timeout)
