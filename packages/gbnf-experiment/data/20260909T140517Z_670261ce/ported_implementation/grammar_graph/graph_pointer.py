"""Port of ``src/grammar-graph/graph-pointer.ts``."""

from __future__ import annotations

from typing import Any, Iterator, List, Optional, Tuple

from .colorize import colorize
from .graph_node import GraphNode
from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


# Resolving a grammar whose repetition can match the empty string (`a ::= "b"?`
# used as `a*`) never terminates: it keeps nesting pointers forever. The reference
# runs out of Javascript call stack and throws; this is the equivalent bound, kept
# well above any depth a real grammar reaches.
MAX_POINTER_DEPTH = 5000


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional["GraphPointer"] = None):
        if node is None:
            raise ValueError("Node is undefined")
        self.node = node
        self.parent = parent
        self._valid: Optional[bool] = None
        self.id = f"{parent.id}-{node.id}" if parent is not None else node.id
        self.depth = parent.depth + 1 if parent is not None else 0
        self.print = print_graph_pointer(self)

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """
        1. If the current node is an end node, and the pointer has a parent, return the
           parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_
           resolved is true, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none
           exists, throw an error.

        The reference recurses here; this walks an explicit stack instead (same
        depth-first order) because a recursive generator overruns Python's much
        shallower recursion limit on deeply nested grammars.
        """
        stack: List[Tuple["GraphPointer", bool]] = [(self, resolved)]
        while stack:
            pointer, is_resolved = stack.pop()
            if is_graph_pointer_rule_ref(pointer):
                if is_resolved:
                    if pointer.node.next is None:
                        raise ValueError(f"No next node: {pointer.node!r}")
                    stack.append((GraphPointer(pointer.node.next, pointer.parent), False))
                else:
                    if pointer.depth >= MAX_POINTER_DEPTH:
                        raise RecursionError(
                            "Maximum grammar depth exceeded; the grammar is most likely "
                            "infinitely recursive (for instance a rule that can match "
                            'the empty string used with "*" or "+")'
                        )
                    for node in reversed(pointer.node.rule.nodes):
                        stack.append((GraphPointer(node, pointer), False))
            elif is_graph_pointer_rule_end(pointer):
                if pointer.parent is None:
                    yield pointer
                else:
                    stack.append((pointer.parent, True))
            elif is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(
                pointer
            ):
                yield pointer
            else:
                raise ValueError(f"Unknown rule: {pointer.node.rule!r}")

    def fetch_next(self) -> Iterator["GraphPointer"]:
        pointer: Optional["GraphPointer"] = self
        while pointer is not None:
            # if this pointer is invalid, then we don't return any new pointers
            if pointer._valid is False:
                return

            # if this pointer is an end node, we return the parent's next node. If no
            # parent exists, we return nothing, since it's the end of the line.
            if is_rule_end(pointer.node.rule):
                pointer = pointer.parent
                continue

            if pointer.node.next is None:
                raise ValueError(f"No next node: {pointer.node!r}")
            yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
            return

    @property
    def rule(self) -> Any:
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return self.print(colorize=colorize)

    # Camel-cased alias mirroring the reference method name.
    fetchNext = fetch_next
