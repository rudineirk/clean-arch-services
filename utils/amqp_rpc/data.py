from http import HTTPStatus
from typing import Any, List

from dataclasses import dataclass


@dataclass
class RawRpcResp:
    payload: str
    content_type: str


@dataclass
class RawRpcCall:
    route: str
    payload: str
    content_type: str


@dataclass
class RpcCall:
    service: str
    method: str
    args: List[Any]


@dataclass
class RpcResp:
    status: int
    body: Any

    @property
    def ok(self):
        return self.status == HTTPStatus.OK
