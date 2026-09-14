from typing import Generator, Optional

from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


class GraphPointer:
    def __init__(self, node, parent: Optional["GraphPointer"] = None):
        if node is None:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent else node.id
        self.__valid__ = None

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self):
        return self.__valid__

    @valid.setter
    def valid(self, valid) -> None:
        self.__valid__ = valid

    def print(self, **opts) -> str:
        return print_graph_pointer(self, **opts)

    def resolve(self, resolved: bool = False) -> Generator["GraphPointer", None, None]:
        """Resolve the graph pointer.

        `resolved` indicates whether the pointer has already been resolved.
        Yields the resolved graph pointers.
        """
        if is_graph_pointer_rule_ref(self):
            if resolved:
                if not self.node.next:
                    raise ValueError(f"No next node: {self.node}")
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in self.rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_graph_pointer_rule_end(self):
            if not self.parent:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_graph_pointer_rule_char(self) or is_graph_pointer_rule_char_exclude(
            self
        ):
            yield self
        else:
            raise ValueError(f"Unknown rule: {self.node.rule}")

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
                raise ValueError(f"No next node: {self.node}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()

    def __repr__(self) -> str:
        return f"<GraphPointer {self.id} {self.node}>"
