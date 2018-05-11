import msgpack

from simple_amqp import AmqpMsg

from .data import Event

CONTENT_TYPE_MSGPACK = 'application/msgpack'


def encode_event(event: Event) -> AmqpMsg:
    payload = msgpack.packb({
        'service': event.service,
        'topic': event.topic,
        'payload': event.payload,
    })
    return AmqpMsg(
        payload=payload,
        content_type=CONTENT_TYPE_MSGPACK,
    )


def decode_event(msg: AmqpMsg) -> Event:
    payload = msgpack.unpackb(msg.payload, encoding='utf8')
    return Event(
        service=payload['service'],
        topic=payload['topic'],
        payload=payload['payload'],
    )
