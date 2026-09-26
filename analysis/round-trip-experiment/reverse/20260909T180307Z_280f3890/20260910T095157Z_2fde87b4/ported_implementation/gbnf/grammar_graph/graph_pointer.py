from typing import Iterator, Optional

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
            raise Exception("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent is not None else node.id
        self._valid: Optional[bool] = None

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: Optional[bool]) -> None:
        self._valid = valid

    def print(self, opts) -> str:
        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """Resolve this pointer into concrete, non-reference pointers.

        `resolved` records whether the pointer has already been resolved.
        """
        pointer = self
        if is_graph_pointer_rule_ref(pointer):
            if resolved:
                next_node = pointer.node.next
                if next_node is None:
                    raise Exception(f"No next node: {pointer.node.id}")
                yield from GraphPointer(next_node, pointer.parent).resolve()
            else:
                for node in pointer.rule.nodes:
                    yield from GraphPointer(node, pointer).resolve()
        elif is_graph_pointer_rule_end(pointer):
            if pointer.parent is None:
                yield pointer
            else:
                yield from pointer.parent.resolve(True)
        elif is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(
            pointer
        ):
            yield pointer
        else:
            raise Exception(f"Unknown rule: {pointer.rule!r}")

    def fetch_next(self) -> Iterator["GraphPointer"]:
        """Fetch the pointers that follow this one."""
        # If this pointer is invalid, then we don't return any new pointers
        if not self.valid:
            return

        # If this pointer is an end node, we return the parent's next node.
        # If no parent exists, we return nothing, since it's the end of the line.
        if is_rule_end(self.node.rule):
            if self.parent is not None:
                yield from self.parent.fetch_next()
        else:
            next_node = self.node.next
            if next_node is None:
                raise Exception(f"No next node: {self.node.id}")
            yield from GraphPointer(next_node, self.parent).resolve()
