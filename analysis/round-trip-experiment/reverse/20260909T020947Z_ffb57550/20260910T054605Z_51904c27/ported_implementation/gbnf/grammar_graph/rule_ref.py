from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from .rule_type import RuleType

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.type = RuleType.REF
        self.value = value
        # An insertion ordered set of nodes, patched in once the graph is built.
        self._nodes: Optional[Dict["GraphNode", None]] = None

    @property
    def nodes(self) -> Dict["GraphNode", None]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = dict.fromkeys(nodes)

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
