import traceback
from typing import Callable, Tuple

from simple_amqp import AmqpParameters

from .client import RpcClient
from .conn import AmqpRpcConn
from .data import (
    CALL_ARGS_MISMATCH,
    CALL_ERROR,
    METHOD_NOT_FOUND,
    OK,
    RPC_CALL_TIMEOUT,
    SERVICE_NOT_FOUND,
    RpcCall,
    RpcResp
)


class AmqpRpc(AmqpRpcConn):
    def __init__(
            self,
            params: AmqpParameters,
            route: str='service.name',
            call_timeout=RPC_CALL_TIMEOUT,
    ):
        super().__init__(
            params=params,
            route=route,
            call_timeout=call_timeout,
            rpc_callback=self.rpc_callback,
        )
        self.services = {}

    def add_svc(self, service) -> 'AmqpRpc':
        self.services[service.svc.name] = \
            service.svc.get_methods(service)

        return self

    def client(self, service: str, route: str) -> RpcClient:
        self.add_publish_route(route)
        return RpcClient(self, service, route)

    def call(self, call: RpcCall) -> RpcResp:
        return self.send_rpc_call(call)

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
