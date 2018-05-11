from typing import Any, Callable, List

from utils.struct import Struct

from .consts import OK


class RpcCall(metaclass=Struct):
    route: str
    service: str
    method: str
    args: List[Any]


class RpcResp(metaclass=Struct):
    status: int
    body: Any = None

    @property
    def ok(self):
        return self.status == OK


RpcCallback = Callable[[RpcCall], RpcResp]
