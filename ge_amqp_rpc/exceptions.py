class AmqpRpcException:
    pass


class ServiceNotFound(AmqpRpcException):
    pass


class MethodNotFound(AmqpRpcException):
    pass
