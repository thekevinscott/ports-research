from __future__ import annotations

from typing import Any, Dict, Optional, Set


class RuleRef:
    def __init__(self, value: int) -> None:
        self.type = "RuleRef"
        self.value = value
        self._nodes: Optional[Set[Any]] = None

    @property
    def nodes(self) -> Set[Any]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Set[Any]) -> None:
        self._nodes = nodes

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.value}

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleRef):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value})"
