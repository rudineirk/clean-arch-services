from pika import SelectConnection, URLParameters

RPC_EXCHANGE = 'rpc.{route}'
RPC_QUEUE = 'rpc.{route}'


class AmqpRpc:
    def __init__(self, amqp_url, route='service.name'):
        self.amqp_url = amqp_url
        self.conn = None
        self.publish_channel = None
        self.listen_channel = None
        self.resp_channel = None

        self.route = route
        self.listen_services = {}
        self.publish_routes = set()

        self._response_futures = {}
        self._resp_queue = ''
        self._resp_consumer_tag = ''
        self._listen_consumer_tag = ''
        self._closing = False

    def add_service(self, service):
        self.listen_services[service.svc.name] = service.svc.get_methods()
        return self

    def add_client(self, client):
        self.publish_services.add(client.route)
        return self

    def disconnect(self):
        self._closing = True
        self.stop_consuming()

    def connect(self):
        self._closing = False
        self.conn = SelectConnection(
            URLParameters(self.amqp_url),
            self.on_connection_open,
            stop_ioloop_on_close=False,
        )
        self.conn.ioloop.start()

    def reconnect(self):
        if self._closing:
            return

        self.connect()

    def open_channels(self):
        self.conn.channel(on_open_callback=self.on_publish_channel_open)
        self.conn.channel(on_open_callback=self.on_listen_channel_open)
        self.conn.channel(on_open_callback=self.on_resp_channel_open)

    def close_channels(self):
        if self.publish_channel:
            self.publish_channel.close()
        if self.listen_channel:
            self.listen_channel.close()

    def stop_consuming(self):
        self.listen_channel.basic_cancel(
            self._listen_consumer_tag,
            self.on_listen_cancel_ok,
        )
        self.resp_channel.basic_cancel(
            self._resp_consumer_tag,
            self.on_resp_cancel_ok,
        )

    def create_publish_exchanges(self):
        for route in self.publish_routes:
            exchange = RPC_EXCHANGE.format(route=route)
            self.publish_channel.exchange_declare(
                exchange, 'topic',
                durable=True,
            )

    def create_listen_exchanges(self):
        exchange = RPC_EXCHANGE.format(route=self.route)
        self.listen_channel.exchange_declare(
            exchange, 'topic',
            durable=True,
            callback=self.on_listen_exchange_declare_ok,
        )

    def create_listen_queue(self):
        queue = RPC_QUEUE.format(route=self.route)
        self.listen_channel.queue_declare(
            queue, durable=True,
            callback=self.on_listen_queue_declare_ok,
        )

    def bind_listen_queue(self):
        queue = RPC_QUEUE.format(route=self.route)
        exchange = RPC_EXCHANGE.format(route=self.route)
        self.listen_channel.queue_bind(
            queue,
            exchange,
            routing_key='rpc.call',
            callback=self.on_listen_bind_ok,
        )

    def start_listen_handler(self):
        queue = RPC_QUEUE.format(route=self.route)
        self._listen_consumer_tag = self.listen_channel.basic_consume(
            queue,
            callback=self.on_listen_message,
        )

    def create_resp_queue(self):
        self.resp_channel.queue_declare(
            '',
            auto_delete=True,
            exclusive=True,
            callback=self.on_resp_queue_declare_ok,
        )

    def start_resp_handler(self):
        self._resp_consumer_tag = self.resp_channel.basic_consume(
            self._resp_queue,
            auto_ack=True,
            exclusive=True,
            callback=self.on_resp_message,
        )

    def on_connection_open(self, connection):
        self.conn.add_on_close_callback(self.on_connection_closed)
        self.open_channels()

    def on_connection_closed(self, connection, reply_code, reply_text):
        self.publish_channel = None
        self.listen_channel = None
        for fut in self._response_futures.values():
            fut.cancel()

        self._consumer_tags = {}
        self._response_futures = {}
        self._resp_queue = ''
        self._resp_consumer_tag = ''
        if self._closing:
            self.conn.ioloop.stop()
            return

        self._connection.add_timeout(5, self.reconnect)

    def on_publish_channel_open(self, channel):
        self.publish_channel = channel
        channel.add_on_close_callback(self.on_publish_channel_closed)
        self.create_publish_exchanges()

    def on_listen_channel_open(self, channel):
        self.listen_channel = channel
        channel.add_on_close_callback(self.on_listen_channel_closed)
        self.create_listen_exchanges()

    def on_resp_channel_open(self, channel):
        self.resp_channel = channel
        channel.add_on_close_callback(self.on_resp_channel_closed)
        self.create_resp_queue()

    def on_publish_channel_closed(self, channel, reply_code, reply_text):
        self.publish_channel = None
        if not self.listen_channel and not self.resp_channel:
            self.conn.close()

    def on_listen_channel_closed(self, channel, reply_code, reply_text):
        self.listen_channel = None
        if not self.publish_channel and not self.resp_channel:
            self.conn.close()

    def on_resp_channel_closed(self, channel, reply_code, reply_text):
        self.resp_channel = None
        if not self.publish_channel and not self.listen_channel:
            self.conn.close()

    def on_listen_exchange_declare_ok(self, frame):
        self.create_listen_queue()

    def on_listen_queue_declare_ok(self, frame):
        self.bind_listen_queue()

    def on_listen_queue_bind_ok(self, frame):
        self.start_listen_handler()

    def on_resp_queue_declare_ok(self, frame):
        self._resp_queue = frame.queue
        self.start_resp_handler()

    def on_listen_cancel_ok(self, frame):
        self._listen_consumer_tag = ''
        if not self._resp_consumer_tag:
            self.close_channels()

    def on_resp_cancel_ok(self, frame):
        self._resp_consumer_tag = ''
        if not self._listen_consumer_tag:
            self.close_channels()

    def on_listen_message(self, channel, deliver, props, body):
        # TODO: implement message handling
        pass

    def on_resp_message(self, channel, deliver, props, body):
        # TODO: implement message handling
        pass
