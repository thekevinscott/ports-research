from __future__ import annotations

from typing import Iterator, Set

from .get_serialized_rule_key import get_serialized_rule_key
from .graph import Graph, Pointers
from .types import ResolvedRule, ValidInput


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        return self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: Set[str] = set()
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

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
