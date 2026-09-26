from __future__ import annotations

from typing import TYPE_CHECKING

from .grammar_graph_types import RuleType

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int) -> None:
        self.type = RuleType.REF
        self.value = value
        self._nodes: set[GraphNode] | None = None

    @property
    def nodes(self) -> set[GraphNode]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: set[GraphNode]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
