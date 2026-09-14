from __future__ import annotations

from typing import Iterator, Optional

from .print import print_graph_pointer
from .type_guards import is_rule_char, is_rule_char_exclude, is_rule_end, is_rule_ref
from .types import PrintOpts


class GraphPointer:
    def __init__(self, node, parent: Optional['GraphPointer'] = None):
        if node is None:
            raise ValueError('Node is undefined')
        self.node = node
        self.parent = parent
        self.id: str = f'{parent.id}-{node.id}' if parent is not None else node.id
        self.valid: Optional[bool] = None

    @property
    def rule(self):
        return self.node.rule

    def print(self, opts: PrintOpts) -> str:
        return print_graph_pointer(self)(opts)

    def resolve(self, resolved: bool = False) -> Iterator['GraphPointer']:
        """Resolve this pointer into pointers that sit on concrete (non-reference) rules.

        :param resolved: whether the pointer has already been resolved
        """
        rule = self.rule
        if is_rule_ref(rule):
            if resolved:
                if self.node.next is None:
                    raise ValueError(f'No next node: {self.node.meta!r}')
                yield from GraphPointer(self.node.next, self.parent).resolve()
            else:
                for node in rule.nodes:
                    yield from GraphPointer(node, self).resolve()
        elif is_rule_end(rule):
            if self.parent is None:
                yield self
            else:
                yield from self.parent.resolve(True)
        elif is_rule_char(rule) or is_rule_char_exclude(rule):
            yield self
        else:
            raise ValueError(f'Unknown rule: {rule!r}')

    def fetch_next(self) -> Iterator['GraphPointer']:
        """Fetch the pointers that follow this one, if this pointer is still valid."""
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
                raise ValueError(f'No next node: {self.node.meta!r}')
            yield from GraphPointer(self.node.next, self.parent).resolve()

    def __repr__(self) -> str:
        return f'GraphPointer({self.id})'
