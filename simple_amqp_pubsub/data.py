from typing import Any

from utils.struct import Struct


class Event(metaclass=Struct):
    service: str
    topic: str
    payload: Any
    retry_count: int = 0
