from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterable, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule; resolved to concrete nodes by the `Graph`."""

    __slots__ = ('value', '_nodes')

    def __init__(self, value: int):
        self.value = value
        # An insertion-ordered set of nodes, mirroring JS `Set`.
        self._nodes: Optional[Dict['GraphNode', None]] = None

    @property
    def nodes(self) -> Iterable['GraphNode']:
        if self._nodes is None:
            raise ValueError('Nodes are not set')
        return self._nodes.keys()

    @nodes.setter
    def nodes(self, nodes: Iterable['GraphNode']) -> None:
        self._nodes = {node: None for node in nodes}

    def __repr__(self) -> str:
        return f'RuleRef({self.value})'
