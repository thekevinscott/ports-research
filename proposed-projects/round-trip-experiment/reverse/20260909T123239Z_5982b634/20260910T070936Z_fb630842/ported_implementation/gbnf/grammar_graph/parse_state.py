from __future__ import annotations

from typing import Iterator, Set

from .get_serialized_rule_key import get_serialized_rule_key
from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator:
        return self.rules()

    def rules(self) -> Iterator:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, text: str) -> 'ParseState':
        if not isinstance(text, str):
            raise TypeError('input text must be of type string')
        return ParseState(self._graph, self._graph.add(text, self._pointers))

    def __add__(self, text: str) -> 'ParseState':
        return self.add(text)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f'ParseState({list(self.rules())!r})'
