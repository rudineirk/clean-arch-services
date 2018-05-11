import traceback

from simple_amqp import AmqpMsg, AmqpParameters
from simple_amqp.gevent import GeventAmqpConnection
from simple_amqp_pubsub import Event
from simple_amqp_pubsub.base import BaseAmqpPubSub


class GeventAmqpPubSub(BaseAmqpPubSub):
    def start(self, auto_reconnect: bool=True, wait: bool=True):
        self.conn.start(auto_reconnect, wait)

    def stop(self):
        self.conn.stop()

    def _create_conn(self, params: AmqpParameters):
        return GeventAmqpConnection(params)

    def recv_event(self, event: Event):
        method, error = self._get_handler(event.service, event.topic)
        if error:
            return error

        try:
            method(event.payload)
        except Exception as e:
            if not self._recv_error_handlers:
                traceback.print_exc()
            else:
                for handler in self._recv_error_handlers:
                    handler(e)

    def _send_event_msg(self, msg: AmqpMsg):
        self._publish_channel.publish(msg)

    def _on_event_message(self, msg: AmqpMsg) -> bool:
        event = self._decode_event(msg)
        resp = self.recv_event(event)
        if resp is not None:
            return False
        return True
