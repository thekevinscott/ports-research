from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from .colorize import colorize as default_colorize
from .graph_node import GraphNode
from .print import print_graph_pointer
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_rule_end,
)


# How much deeper than its starting point a single `resolve` walk may descend.
# Descending means stepping into a rule reference without consuming any input,
# which a well-formed grammar can only do as many times as it has nested rules.
# A grammar that can match the empty string inside a repetition — `("a"*)+`, say
# — descends forever instead; the reference implementation blows the JS stack
# there, and this bound is how the port fails fast on the same grammars.
MAX_RESOLVE_DEPTH_GROWTH = 1000


class GraphPointer:
    def __init__(self, node: GraphNode, parent: "GraphPointer | None" = None):
        if node is None:
            raise RuntimeError('Node is undefined')
        self.node = node
        self.parent = parent
        self.id = f'{parent.id}-{node.id}' if parent else node.id
        self.depth = parent.depth + 1 if parent is not None else 0
        self._valid: bool | None = None

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """
        1. If the current node is an end node, and the pointer has a parent, return the parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved is true, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none exists, throw an error.

        Walked with an explicit stack rather than recursively: the parent chain
        grows with the depth of the parse, which is unbounded, and Python's
        recursion limit is far lower than a JS engine's stack.
        """
        # LIFO, so pushing the referenced nodes in reverse keeps the depth-first
        # order the recursive form yields in.
        max_depth = self.depth + MAX_RESOLVE_DEPTH_GROWTH
        stack: list[tuple["GraphPointer", bool]] = [(self, resolved)]
        while stack:
            pointer, is_resolved = stack.pop()
            if pointer.depth > max_depth:
                raise RecursionError(
                    'Maximum rule depth exceeded; the grammar can descend into a rule '
                    'without consuming input, e.g. a repetition of an optional rule')
            if is_graph_pointer_rule_ref(pointer):
                if is_resolved:
                    if not pointer.node.next:
                        raise RuntimeError(f'No next node: {pointer.node!r}')
                    stack.append((GraphPointer(pointer.node.next, pointer.parent), False))
                else:
                    for node in reversed(pointer.node.rule.nodes):
                        stack.append((GraphPointer(node, pointer), False))
            elif is_graph_pointer_rule_end(pointer):
                if not pointer.parent:
                    yield pointer
                else:
                    stack.append((pointer.parent, True))
            elif is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(pointer):
                yield pointer
            else:
                raise RuntimeError(f'Unknown rule: {pointer.node.rule!r}')

    def fetch_next(self) -> Iterator["GraphPointer"]:
        pointer: "GraphPointer | None" = self
        while pointer is not None:
            # if this pointer is invalid, then we don't return any new pointers
            if pointer._valid is False:
                return

            # if this pointer is an end node, we return the parent's next node. If no parent exists,
            # we return nothing, since it's the end of the line.
            if is_rule_end(pointer.node.rule):
                pointer = pointer.parent
            else:
                if not pointer.node.next:
                    raise RuntimeError(f'No next node: {pointer.node!r}')
                yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
                return

    @property
    def rule(self) -> Any:
        return self.node.rule

    @property
    def valid(self) -> bool | None:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def print(self, colorize: Callable[..., str] = default_colorize) -> str:
        return print_graph_pointer(self, colorize=colorize)

    def __repr__(self) -> str:
        return self.print()

    # JS-name alias for parity with the reference implementation.
    fetchNext = fetch_next
