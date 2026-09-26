from typing import List, Optional

from .grammar_graph_types import RuleType


class RuleRef:
    def __init__(self, value: int):
        self.type = RuleType.REF
        self.value = value
        self._nodes: Optional[List["object"]] = None

    @property
    def nodes(self) -> List["object"]:
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = list(nodes)

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
