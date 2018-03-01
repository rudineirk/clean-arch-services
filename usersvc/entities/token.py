from typing import List

from dataclasses import dataclass


@dataclass
class Token:
    token: str
    owner: str
    version: int
    ns: str  # namespace
    permissions: List[str]
