from dataclasses import dataclass


@dataclass
class RawRpcResp:
    body: str
    content_type: str
