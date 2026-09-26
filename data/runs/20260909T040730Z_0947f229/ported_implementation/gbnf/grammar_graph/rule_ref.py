"""Port of ``src/grammar-graph/rule-ref.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef:
    __slots__ = ('value', '_nodes')

    def __init__(self, value: int) -> None:
        self.value = value
        self._nodes: Optional[list] = None

    @property
    def nodes(self) -> list:
        if self._nodes is None:
            raise ValueError('Nodes are not set')
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable['GraphNode']) -> None:
        # A list rather than a set: iteration order has to be deterministic, and
        # the reference implementation only ever inserts unique nodes.
        self._nodes = list(nodes)

    def __repr__(self) -> str:
        return f'RuleRef({self.value})'
