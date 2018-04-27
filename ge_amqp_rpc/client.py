from .rpc import AmqpRpc
from .data import RpcCall


class RpcClient:
    def __init__(self, amqp_rpc: AmqpRpc, service: str, route: str):
        self.amqp_rpc = amqp_rpc
        self.service = service
        self.route = route

        self.methods_cache = {}

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass

        try:
            return self.methods_cache[name]
        except KeyError:
            pass

        def rpc_call(*args):
            call = RpcCall(

            )
            self.amqp_rpc.rpc_call()

