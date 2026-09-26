from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A placeholder for a rule defined elsewhere in the grammar.

    The graph resolves every ``RuleRef`` to the nodes it points at once all
    stacks are built; ``RuleRef``s are never exposed to the end user.
    """

    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[list["GraphNode"]] = None

    @property
    def nodes(self) -> list["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list["GraphNode"]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleRef):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(("RuleRef", self.value))
