from typing import List, NamedTuple


class Role(NamedTuple):
    id: int = -1
    name: str
    permissions: List[str]
