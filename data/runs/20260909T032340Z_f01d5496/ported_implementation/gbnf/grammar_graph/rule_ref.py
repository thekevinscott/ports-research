from typing import TYPE_CHECKING, Iterable, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule in the grammar.

    ``nodes`` is kept as an insertion-ordered collection: the order the referenced
    nodes are walked in decides the order rules come back out of a ParseState.
    """

    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        unique: List["GraphNode"] = []
        seen = set()
        for node in nodes:
            if id(node) not in seen:
                seen.add(id(node))
                unique.append(node)
        self._nodes = unique

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
