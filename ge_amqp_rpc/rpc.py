import traceback
from typing import Callable, Tuple

from ge_amqp import AmqpParameters

from .client import RpcClient
from .conn import AmqpRpcConn
from .data import (
    CALL_ARGS_MISMATCH,
    CALL_ERROR,
    METHOD_NOT_FOUND,
    OK,
    SERVICE_NOT_FOUND,
    RpcCall,
    RpcResp
)
from .exceptions import MethodNotFound, ServiceNotFound


class AmqpRpc:
    def __init__(
            self,
            params: AmqpParameters,
            route: str='service.name',
            call_timeout=5,
    ):
        self.conn = AmqpRpcConn(
            params,
            route=route,
            call_timeout=call_timeout,
            rpc_callback=self.rpc_callback,
        )
        self.services = {}

    def start(self, auto_reconnect=True):
        self.conn.start(auto_reconnect)

    def stop(self):
        self.conn.stop()

    def add_svc(self, service) -> 'AmqpRpc':
        self.services[service.svc.name] = \
            service.svc.get_methods(service)

        return self

    def client(self, service: str, route: str) -> RpcClient:
        self.conn.add_publish_route(route)
        return RpcClient(self, service, route)

    def rpc_call(self, call: RpcCall) -> RpcResp:
        return self.conn.rpc_call(call)

    def rpc_callback(self, call: RpcCall) -> RpcResp:
        method, resp = self._get_method(call.service, call.method)
        if method is None:
            return resp

        resp = None
        try:
            resp = method(*call.args)
        except TypeError:
            return RpcResp(
                status=CALL_ARGS_MISMATCH,
                body='Invalid call arguments',
            )
        except Exception:
            traceback.print_exc()
            return RpcResp(
                status=CALL_ERROR,
            )

        return RpcResp(
            status=OK,
            body=resp,
        )

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
