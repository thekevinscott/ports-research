"""Port of ``src/grammar-graph/rule-ref.ts``."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Set

from .types import _Rule

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef(_Rule):
    """A reference to another rule stack; resolved into nodes by ``Graph``."""

    def __init__(self, value: int):
        self.value = value
        self._nodes: "Iterable[GraphNode] | None" = None

    def _key(self):
        return ('ref', self.value)

    @property
    def nodes(self) -> "Set[GraphNode]":
        if self._nodes is None:
            raise ValueError('Nodes are not set')
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: "Iterable[GraphNode]") -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f'RuleRef({self.value!r})'
