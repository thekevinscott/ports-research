from __future__ import annotations

from typing import Iterator, Optional

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
from .types import UnresolvedRule


# A pointer's chain of parents grows as the graph is walked, so the reference's
# recursive `resolve`/`fetchNext` are written iteratively here: Python's much
# smaller call stack would otherwise cap the length of the parsable input.
# The depth guard keeps left-recursive grammars (`foo ::= foo`) from looping
# forever, mirroring the stack overflow the reference raises for them.
MAX_POINTER_DEPTH = 50_000


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional['GraphPointer'] = None):
        if node is None:
            raise Exception('Node is undefined')
        self.node = node
        self.parent = parent
        self.id = f'{parent.id}-{node.id}' if parent else node.id
        self.depth = parent.depth + 1 if parent else 0
        self._valid: Optional[bool] = None
        self.print = print_graph_pointer(self)

    def resolve(self, resolved: bool = False) -> Iterator['GraphPointer']:
        """
        1. If the current node is an end node, and the pointer has a parent, return the parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved is True, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none exists, throw an error.
        """
        # depth-first, in the same order as the reference's recursion
        stack = [(self, resolved)]
        while stack:
            pointer, is_resolved = stack.pop()
            if pointer.depth > MAX_POINTER_DEPTH:
                raise RecursionError('maximum recursion depth exceeded')
            if is_graph_pointer_rule_ref(pointer):
                if is_resolved:
                    if pointer.node.next is None:
                        raise Exception(f'No next node: {pointer.node!r}')
                    stack.append((GraphPointer(pointer.node.next, pointer.parent), False))
                else:
                    children = [GraphPointer(node, pointer) for node in pointer.node.rule.nodes]
                    for child in reversed(children):
                        stack.append((child, False))
            elif is_graph_pointer_rule_end(pointer):
                if not pointer.parent:
                    yield pointer
                else:
                    stack.append((pointer.parent, True))
            elif is_graph_pointer_rule_char(pointer) or is_graph_pointer_rule_char_exclude(pointer):
                yield pointer
            else:
                raise Exception(f'Unknown rule: {pointer.node.rule!r}')

    def fetch_next(self) -> Iterator['GraphPointer']:
        pointer: Optional['GraphPointer'] = self
        while pointer is not None:
            # if this pointer is invalid, then we don't return any new pointers
            if pointer._valid is False:
                return

            # if this pointer is an end node, we return the parent's next node. If no parent exists,
            # we return nothing, since it's the end of the line.
            if is_rule_end(pointer.node.rule):
                pointer = pointer.parent
            else:
                if pointer.node.next is None:
                    raise Exception(f'No next node: {pointer.node!r}')
                yield from GraphPointer(pointer.node.next, pointer.parent).resolve()
                return

    @property
    def rule(self) -> UnresolvedRule:
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def __repr__(self) -> str:
        return self.print(colorize=colorize)


GraphPointerKey = str
