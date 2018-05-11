from abc import ABCMeta
from typing import Callable, Tuple

from simple_amqp_rpc.consts import METHOD_NOT_FOUND, SERVICE_NOT_FOUND
from simple_amqp_rpc.data import RpcCall, RpcResp

from .client import RpcClient


class BaseRpc(metaclass=ABCMeta):
    def __init__(self):
        self.services = {}
        self._recv_error_handlers = set()

    def method(self, service, name=None):
        if service not in self.services:
            self.services[service] = {}

        def decorator(func, name=name):
            if name is None:
                name = func.__name__

            self.services[service][name] = func

        return decorator

    def add_svc(self, service) -> 'BaseRpc':
        self.services[service.svc.name] = \
            service.svc.get_methods(service)

        return self

    def client(self, service: str) -> RpcClient:
        raise NotImplementedError

    def send_call(self, call: RpcCall) -> RpcResp:
        raise NotImplementedError

    def recv_call(self, call: RpcCall) -> RpcResp:
        raise NotImplementedError

    def add_recv_call_error_handler(self, handler):
        self._recv_error_handler.add(handler)

    def _get_method(
            self,
            service_name: str,
            method_name: str,
    ) -> Tuple[Callable, RpcResp]:
        try:
            service = self.services[service_name]
        except KeyError:
            msg = 'Service [{}] not found'.format(
                service_name,
            )
            return None, RpcResp(
                status=SERVICE_NOT_FOUND,
                body=msg,
            )

        try:
            method = service[method_name]
        except KeyError:
            msg = 'Method [{}->{}] not found'.format(
                service_name,
                method_name,
            )
            return None, RpcResp(
                status=METHOD_NOT_FOUND,
                body=msg,
            )

        return method, None
