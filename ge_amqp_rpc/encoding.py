import msgpack

from ge_amqp import AmqpMsg

from .data import RpcCall, RpcResp

CONTENT_TYPE_MSGPACK = 'application/msgpack'


def encode_rpc_call(call: RpcCall) -> AmqpMsg:
    payload = msgpack.packb({
        'service': call.service,
        'method': call.method,
        'args': call.args,
    })
    return AmqpMsg(
        payload=payload,
        content_type=CONTENT_TYPE_MSGPACK,
    )


def decode_rpc_call(msg: AmqpMsg) -> RpcCall:
    payload = msgpack.unpackb(msg.payload)
    return RpcCall(
        service=payload['service'],
        method=payload['method'],
        args=payload['args'],
    )


def encode_rpc_resp(resp: RpcResp) -> AmqpMsg:
    payload = msgpack.packb({
        'status': resp.status,
        'body': resp.body,
    })
    return AmqpMsg(
        payload=payload,
        content_type=CONTENT_TYPE_MSGPACK,
    )


def decode_rpc_resp(msg: AmqpMsg) -> RpcResp:
    payload = msgpack.unpackb(msg.payload)
    return RpcResp(
        status=payload['status'],
        body=payload['body'],
    )
