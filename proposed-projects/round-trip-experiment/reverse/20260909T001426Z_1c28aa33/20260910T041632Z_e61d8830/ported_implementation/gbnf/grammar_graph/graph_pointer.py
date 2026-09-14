from typing import Iterator, Optional

from .graph_node import GraphNode
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional["GraphPointer"] = None):
        if node is None:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent else node.id
        self._valid: Optional[bool] = None

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def print(self, opts) -> str:
        from .print import print_graph_pointer

        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """Resolve the graph pointer.

        `resolved` records whether the pointer has already been resolved.
        Yields the resolved graph pointers.
        """
        if is_graph_pointer_rule_ref(self):
            if resolved:
                if self.node.next is None:
                    raise ValueError(f"No next node: {self.node.id}")
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in self.node.rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_graph_pointer_rule_end(self):
            if self.parent is None:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_graph_pointer_rule_char(self) or is_graph_pointer_rule_char_exclude(
            self
        ):
            yield self
        else:
            raise ValueError(f"Unknown rule: {self.node.rule}")

    def fetch_next(self) -> Iterator["GraphPointer"]:
        """Fetch the next resolved graph pointers."""
        # If this pointer is invalid, then we don't return any new pointers
        if not self.valid:
            return

        # If this pointer is an end node, we return the parent's next node.
        # If no parent exists, we return nothing, since it's the end of the line.
        if is_rule_end(self.node.rule):
            if self.parent is not None:
                yield from self.parent.fetch_next()
        else:
            if self.node.next is None:
                raise ValueError(f"No next node: {self.node.id}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()

    def __repr__(self) -> str:
        return f"GraphPointer({self.id})"
