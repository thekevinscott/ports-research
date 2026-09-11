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

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
