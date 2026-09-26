from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        # a list rather than a set: JS sets iterate in insertion order, and the
        # order the referenced nodes are visited in decides the order rules come
        # back out of the graph.
        self._nodes: list["GraphNode"] | None = None

    @property
    def nodes(self) -> list["GraphNode"]:
        if self._nodes is None:
            raise RuntimeError('Nodes are not set')
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list["GraphNode"]) -> None:
        self._nodes = list(nodes)

    def __repr__(self) -> str:
        return f'RuleRef({self.value})'
