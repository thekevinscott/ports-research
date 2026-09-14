from typing import TYPE_CHECKING, Dict, List, Optional

from .rule_type import RuleType

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    RULE_TYPE = RuleType.REF

    def __init__(self, value: int):
        self.type = RuleType.REF
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List["GraphNode"]) -> None:
        self._nodes = list(nodes)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    def __hash__(self) -> int:
        return hash((RuleType.REF, self.value))

    def to_json(self) -> Dict[str, object]:
        return {"type": self.type.value, "value": self.value}

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
