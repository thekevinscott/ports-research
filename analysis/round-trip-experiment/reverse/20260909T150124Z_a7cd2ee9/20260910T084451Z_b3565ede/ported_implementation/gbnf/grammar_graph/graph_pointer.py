from typing import Iterator

from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


class GraphPointer:
    def __init__(self, node, parent=None) -> None:
        if not node:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self.id = f"{parent.id}-{node.id}" if parent is not None else node.id
        self._valid: bool | None = None

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self) -> bool | None:
        return self._valid

    @valid.setter
    def valid(self, valid: bool | None) -> None:
        self._valid = valid

    def print(self, opts) -> str:
        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """Resolve the graph pointer, yielding the resolved graph pointers."""
        pointer = self
        if is_graph_pointer_rule_ref(pointer):
            if resolved:
                if pointer.node.next is None:
                    raise ValueError(f"No next node: {pointer.node}")
                yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
            else:
                for node in pointer.node.rule.nodes:
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
            raise ValueError(f"Unknown rule: {pointer.node.rule}")

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
                raise ValueError(f"No next node: {self.node}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()

    def __repr__(self) -> str:
        return f"GraphPointer(id={self.id!r})"
