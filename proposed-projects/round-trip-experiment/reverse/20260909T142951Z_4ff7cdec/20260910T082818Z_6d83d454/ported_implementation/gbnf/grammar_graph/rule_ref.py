from typing import List, Optional

from .grammar_graph_types import RuleType


class RuleRef:
    def __init__(self, value: int):
        self.type = RuleType.REF
        self._nodes: Optional[List["object"]] = None
        self.value = value

    @property
    def nodes(self) -> List["object"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List["object"]) -> None:
        # Nodes are stored in path order; iteration order is what makes pointer
        # resolution — and therefore the order rules are yielded in — deterministic.
        self._nodes = list(nodes)

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
