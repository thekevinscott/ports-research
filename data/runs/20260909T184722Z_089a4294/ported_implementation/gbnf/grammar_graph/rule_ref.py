from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: list["GraphNode"] | None = None

    @property
    def nodes(self) -> list["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        # a unique, insertion-ordered collection of nodes
        self._nodes = list(dict.fromkeys(nodes))

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
