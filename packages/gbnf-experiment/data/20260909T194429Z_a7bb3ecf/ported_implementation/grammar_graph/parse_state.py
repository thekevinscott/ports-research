from __future__ import annotations

import json
from typing import TYPE_CHECKING, Iterator, Set

from .types import ResolvedRule, ValidInput

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .generic_set import GenericSet
    from .graph import Graph


class ParseState:
    def __init__(self, graph: 'Graph', pointers: 'GenericSet'):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> 'ParseState':
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        rules: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.to_dict(), separators=(',', ':'))
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, input: ValidInput) -> 'ParseState':
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
