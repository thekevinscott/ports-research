from typing import Iterator, Optional

from .grammar_graph_types import PrintOpts, UnresolvedRule
from .graph_node import GraphNode
from .print import print_graph_pointer
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
        self.valid: Optional[bool] = None

    @property
    def rule(self) -> UnresolvedRule:
        return self.node.rule

    def print(self, opts: PrintOpts) -> str:
        return print_graph_pointer(self, opts)

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """Walk this pointer down to the concrete (char / char-exclude /
        terminal end) pointers it stands for.

        :param resolved: whether the pointer has already been resolved.
        """
        if is_graph_pointer_rule_ref(self):
            if resolved:
                if self.node.next is None:
                    raise ValueError(f"No next node: {self.node.rule!r}")
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
            raise ValueError(f"Unknown rule: {self.node.rule!r}")

    def fetch_next(self) -> Iterator["GraphPointer"]:
        """Yields the next resolved graph pointers that follow this one."""
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
                raise ValueError(f"No next node: {self.node.rule!r}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()
