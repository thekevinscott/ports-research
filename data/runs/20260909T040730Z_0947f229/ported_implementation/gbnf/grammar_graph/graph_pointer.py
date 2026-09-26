"""Port of ``src/grammar-graph/graph-pointer.ts``."""

from __future__ import annotations

from typing import Callable, Iterator, List, Optional, Tuple, Union

from .colorize import Color, colorize
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

Colorize = Callable[[Union[str, int], Color], str]


class GraphPointer:
    __slots__ = ('node', 'parent', '_valid', 'id')

    def __init__(self, node: GraphNode, parent: Optional['GraphPointer'] = None) -> None:
        if node is None:
            raise ValueError('Node is undefined')
        self.node = node
        self.parent = parent
        self._valid: Optional[bool] = None
        self.id = f'{parent.id}-{node.id}' if parent is not None else node.id

    def resolve(self, resolved: bool = False) -> Iterator['GraphPointer']:
        """
        1. If the current node is an end node, and the pointer has a parent, return the
           parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_
           resolved is true, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none
           exists, throw an error.

        The reference implementation recurses. Here the walk uses an explicit stack:
        a pointer's parent chain grows with every repetition of a self-referential
        rule, so recursing would exhaust Python's much smaller stack on long inputs.
        The stack is LIFO with children pushed in reverse, which reproduces the
        original's depth-first, left-to-right yield order.
        """
        stack: List[Tuple['GraphPointer', bool]] = [(self, resolved)]
        while stack:
            pointer, is_resolved = stack.pop()
            if is_graph_pointer_rule_ref(pointer):
                if is_resolved:
                    if pointer.node.next is None:
                        raise ValueError(f'No next node: {pointer.node!r}')
                    stack.append((GraphPointer(pointer.node.next, pointer.parent), False))
                else:
                    stack.extend(
                        (GraphPointer(node, pointer), False)
                        for node in reversed(pointer.node.rule.nodes)
                    )
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
                raise ValueError(f'Unknown rule: {pointer.node.rule!r}')

    def fetch_next(self) -> Iterator['GraphPointer']:
        # Walks up the parent chain iteratively, for the same reason `resolve` does.
        pointer: Optional['GraphPointer'] = self
        while pointer is not None:
            # if this pointer is invalid, then we don't return any new pointers
            if pointer._valid is False:
                return

            # if this pointer is an end node, we return the parent's next node. If no
            # parent exists, we return nothing, since it's the end of the line.
            if is_rule_end(pointer.node.rule):
                pointer = pointer.parent
            else:
                if pointer.node.next is None:
                    raise ValueError(f'No next node: {pointer.node!r}')
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

    def print(self, colorize: Colorize = colorize) -> str:
        return print_graph_pointer(self, colorize)

    def __repr__(self) -> str:
        return self.print(colorize)
