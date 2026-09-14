from typing import TYPE_CHECKING, Dict, Iterable, Iterator, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class NodeSet:
    """An insertion ordered, identity based set of nodes."""

    def __init__(self, nodes: Iterable["GraphNode"] = ()):
        self._nodes: Dict[int, "GraphNode"] = {}
        for node in nodes:
            self.add(node)

    def add(self, node: "GraphNode") -> None:
        self._nodes.setdefault(id(node), node)

    def __iter__(self) -> Iterator["GraphNode"]:
        return iter(list(self._nodes.values()))

    def __len__(self) -> int:
        return len(self._nodes)


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[NodeSet] = None

    @property
    def nodes(self) -> NodeSet:
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: NodeSet) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
