from .base import AmqpConnection


class GeventAmqpConnection(AmqpConnection):
    def configure(self):
        pass

    def start(self, auto_reconnect=True):
        pass

    def stop(self):
        pass
