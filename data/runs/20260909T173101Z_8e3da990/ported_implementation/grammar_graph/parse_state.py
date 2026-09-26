from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .get_serialized_rule_key import get_serialized_rule_key
from .types import ResolvedRule, ValidInput

if TYPE_CHECKING:
    from .graph import Graph, Pointers


class ParseState:
    """An immutable snapshot of a parse.

    Iterate it for the rules that could match next; call it (or `add`) with more
    input to get the next state.
    """

    def __init__(self, graph: "Graph", pointers: "Pointers"):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        rules: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, input: ValidInput) -> "ParseState":
        pointers = self._graph.add(input, self._pointers)
        return ParseState(self._graph, pointers)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f'ParseState({list(self.rules())!r})'
