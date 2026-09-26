"""Port of ``src/grammar-graph/parse-state.ts``.

The TypeScript class extends ``Function`` and wraps itself in a Proxy so the
state is callable; in Python ``__call__`` does the same job directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, List, Set

from .types import ResolvedRule, serialize_rule

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph import Graph, Pointers


class ParseState:
    __slots__ = ('_graph', '_pointers')

    def __init__(self, graph: 'Graph', pointers: 'Pointers') -> None:
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: str) -> 'ParseState':
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        return self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = serialize_rule(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input: str) -> 'ParseState':
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
        rules: List[str] = [repr(rule) for rule in self.rules()]
        return f'ParseState([{", ".join(rules)}])'
