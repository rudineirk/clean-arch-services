from http import HTTPStatus
from typing import Any, Callable, List

from dataclasses import dataclass

OK = HTTPStatus.OK
SERVICE_NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_FOUND = HTTPStatus.METHOD_NOT_ALLOWED
CALL_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR
CALL_ARGS_MISMATCH = HTTPStatus.BAD_REQUEST


@dataclass
class RpcCall:
    route: str
    service: str
    method: str
    args: List[Any]


@dataclass
class RpcResp:
    status: int
    body: Any = None

    @property
    def ok(self):
        return self.status == OK


RpcCallback = Callable[[RpcCall], RpcResp]
