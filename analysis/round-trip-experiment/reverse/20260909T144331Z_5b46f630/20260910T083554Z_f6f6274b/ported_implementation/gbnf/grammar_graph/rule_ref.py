from typing import List, Optional


class RuleRef:
    def __init__(self, value: int):
        self._nodes: Optional[List] = None
        self.value = value

    @property
    def nodes(self) -> List:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = list(nodes)

    @property
    def type(self) -> str:
        return "RuleRef"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    def __hash__(self) -> int:
        return hash(("RuleRef", self.value))
