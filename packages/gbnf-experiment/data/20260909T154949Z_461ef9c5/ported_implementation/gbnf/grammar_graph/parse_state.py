"""Port of ``src/grammar-graph/parse-state.ts``.

The TS class wraps itself in a Proxy so the instance is callable; in Python
``__call__`` gives the same affordance directly.
"""
from __future__ import annotations

from typing import Iterator, List

from .get_serialized_rule_key import get_serialized_rule_key
from .types import ResolvedRule, ValidInput


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        return self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
            if key not in seen:
                seen.add(key)
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

    def as_list(self) -> List[dict]:
        """Convenience: the current rules as plain dicts."""
        return [rule.as_dict() for rule in self.rules()]

    def __repr__(self) -> str:
        return f'ParseState({self.as_list()!r})'
