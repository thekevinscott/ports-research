"""A position in the graph, plus the chain of rule references that led to it."""

from typing import Any, Generator, Optional

from .graph_node import GraphNode
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional["GraphPointer"] = None):
        if not node:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent else node.id
        self._valid: Optional[bool] = None

    @property
    def rule(self) -> Any:
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: Optional[bool]) -> None:
        self._valid = valid

    def print(self, opts: Any) -> str:
        from .print import print_graph_pointer

        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Generator["GraphPointer", None, None]:
        """Resolve the graph pointer, yielding the resolved graph pointers."""
        rule = self.node.rule
        if is_rule_ref(rule):
            if resolved:
                if not self.node.next:
                    raise ValueError(f"No next node: {self.node.id}")
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_rule_end(rule):
            if not self.parent:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_rule_char(rule) or is_rule_char_exclude(rule):
            yield self
        else:
            raise ValueError(f"Unknown rule: {rule}")

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

    def __repr__(self) -> str:
        return f"GraphPointer(id={self.id})"
