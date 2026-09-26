from __future__ import annotations

from typing import Iterator, Optional

from ..utils.errors.gbnf_error import GBNFError
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


class GraphPointer:
    def __init__(self, node: GraphNode, parent: Optional["GraphPointer"] = None):
        if node is None:
            raise GBNFError("Node is undefined")
        self.node = node
        self.parent = parent
        self._valid: Optional[bool] = None
        self.id = f"{parent.id}-{node.id}" if parent else node.id

    def resolve(self, resolved: bool = False) -> Iterator["GraphPointer"]:
        """
        1. If the current node is an end node, and the pointer has a parent, return the
           parent's `fetch_next`; else return nothing.
        2. If the current node is a rule ref, yield the referenced nodes, _unless_ resolved
           is true, in which case it returns next.
        3. If the current node is a char or range, we go to the next node. If none exists,
           throw an error.
        """
        if is_graph_pointer_rule_ref(self):
            if resolved:
                if self.node.next is None:
                    raise GBNFError(f"No next node: {self.node}")
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in self.node.rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_graph_pointer_rule_end(self):
            if not self.parent:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_graph_pointer_rule_char(self) or is_graph_pointer_rule_char_exclude(self):
            yield self
        else:
            raise GBNFError(f"Unknown rule: {self.node.rule}")

    def fetch_next(self) -> Iterator["GraphPointer"]:
        # if this pointer is invalid, then we don't return any new pointers
        if self._valid is False:
            return

        # if this pointer is an end node, we return the parent's next node. If no parent
        # exists, we return nothing, since it's the end of the line.
        if is_rule_end(self.node.rule):
            if self.parent:
                yield from self.parent.fetch_next()
        else:
            if self.node.next is None:
                raise GBNFError(f"No next node: {self.node}")
            pointer = GraphPointer(self.node.next, self.parent)
            yield from pointer.resolve()

    @property
    def rule(self):
        return self.node.rule

    @property
    def valid(self) -> Optional[bool]:
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        self._valid = valid

    def print(self, colorize=default_colorize) -> str:
        return print_graph_pointer(self, colorize)

    def __repr__(self) -> str:
        return self.print(colorize=default_colorize)
