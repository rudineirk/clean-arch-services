from simple_amqp_rpc.data import RpcCall


class GeventRpcClient:
    def __init__(self, amqp_rpc: 'AmqpRpc', service: str, route: str):
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
                route=self.route,
                service=self.service,
                method=name,
                args=args,
            )
            return self.amqp_rpc.call(call)

        self.methods_cache[name] = rpc_call
        return rpc_call
