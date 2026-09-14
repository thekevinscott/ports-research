from typing import Any, Dict, Generator, Optional

from .grammar_graph_types import UnresolvedRule
from .graph_node import GraphNode
from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)

GraphPointerKey = str


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional["GraphPointer"] = None):
        if node is None:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent else node.id
        self.__valid__: Optional[bool] = None

    @property
    def rule(self) -> UnresolvedRule:
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self.__valid__

    @valid.setter
    def valid(self, valid: Optional[bool]) -> None:
        self.__valid__ = valid

    def print(self, opts: Dict[str, Any]) -> str:
        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Generator["GraphPointer", None, None]:
        """Resolve the graph pointer, yielding pointers that point at a
        concrete (non reference) rule.
        """
        pointer = self
        if is_graph_pointer_rule_ref(pointer):
            if resolved:
                if not pointer.node.next:
                    raise ValueError(f"No next node: {pointer.node.id}")
                yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
            else:
                for node in pointer.rule.nodes:
                    yield from GraphPointer(node, pointer).resolve()
        elif is_graph_pointer_rule_end(pointer):
            if not pointer.parent:
                yield pointer
            else:
                yield from pointer.parent.resolve(True)
        elif is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(
            pointer
        ):
            yield pointer
        else:
            raise ValueError(f"Unknown rule: {pointer.node.rule}")

    def fetch_next(self) -> Generator["GraphPointer", None, None]:
        """Fetch the next resolved graph pointers."""
        # If this pointer is invalid, then we don't return any new pointers
        if not self.valid:
            return

        # If this pointer is an end node, we return the parent's next node.
        # If no parent exists, we return nothing, since it's the end of the line.
        if is_rule_end(self.node.rule):
            if self.parent:
                yield from self.parent.fetch_next()
        else:
            if not self.node.next:
                raise ValueError(f"No next node: {self.node.id}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()

    fetchNext = fetch_next

    def __repr__(self) -> str:
        return f"GraphPointer({self.id})"
