from __future__ import annotations

from typing import Iterator

from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


class GraphPointer:
    def __init__(self, node, parent: GraphPointer | None = None) -> None:
        if node is None:
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
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def print(self, opts) -> str:
        from .print import print_graph_pointer

        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Iterator[GraphPointer]:
        """Resolve the graph pointer.

        The reference implementation is recursive throughout. The two branches that
        walk a pointer's parent chain are tail calls, so they are looped here instead:
        that chain grows with every repetition of a `*`/`+` rule, and recursing on it
        would exhaust the interpreter's stack on long runs of repeated input. The
        branching case, where a rule reference fans out over its nodes, stays
        recursive.

        :param resolved: whether the pointer has already been resolved.
        :yields: the resolved graph pointers.
        """
        pointer = self
        while True:
            if is_graph_pointer_rule_ref(pointer):
                if resolved:
                    if pointer.node.next is None:
                        raise ValueError(f"No next node: {pointer.node.id}")
                    pointer = GraphPointer(pointer.node.next, pointer.parent)
                    resolved = False
                    continue
                for node in pointer.node.rule.nodes:
                    yield from GraphPointer(node, pointer).resolve()
                return
            if is_graph_pointer_rule_end(pointer):
                if pointer.parent is None:
                    yield pointer
                    return
                pointer = pointer.parent
                resolved = True
                continue
            if is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(
                pointer,
            ):
                yield pointer
                return
            raise ValueError(f"Unknown rule: {pointer.node.rule}")

    def fetch_next(self) -> Iterator[GraphPointer]:
        """Fetch the next resolved graph pointers.

        :yields: the next resolved graph pointers.
        """
        pointer = self
        while True:
            # If this pointer is invalid, then we don't return any new pointers
            if not pointer.valid:
                return

            # If this pointer is an end node, we return the parent's next node.
            # If no parent exists, we return nothing, since it's the end of the line.
            if is_rule_end(pointer.node.rule):
                if pointer.parent is None:
                    return
                pointer = pointer.parent
                continue

            if pointer.node.next is None:
                raise ValueError(f"No next node: {pointer.node.id}")
            yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
            return
