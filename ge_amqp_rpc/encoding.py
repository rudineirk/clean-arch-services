import msgpack

from .data import RawRpcCall, RawRpcResp, RpcCall, RpcResp

CONTENT_TYPE_MSGPACK = 'application/msgpack'


def encode_rpc_call(call: RpcCall, route: str) -> RawRpcCall:
    payload = msgpack.packb({
        'service': call.service,
        'method': call.method,
        'args': call.args,
    })
    return RawRpcCall(
        route=route,
        payload=payload,
        content_type=CONTENT_TYPE_MSGPACK,
    )


def decode_rpc_call(raw_call: RawRpcCall) -> RpcCall:
    payload = msgpack.unpackb(raw_call.payload)
    return RpcCall(
        service=payload['service'],
        method=payload['method'],
        args=payload['args'],
    )


def encode_rpc_resp(resp: RpcResp) -> RawRpcResp:
    payload = msgpack.packb({
        'status': resp.status,
        'body': resp.body,
    })
    return RawRpcResp(
        payload=payload,
        content_type=CONTENT_TYPE_MSGPACK,
    )


def decode_rpc_resp(raw_resp: RawRpcResp) -> RpcResp:
    payload = msgpack.unpackb(raw_resp.payload)
    return RpcResp(
        status=payload['status'],
        body=payload['body'],
    )
