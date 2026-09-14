from __future__ import annotations

from typing import Iterator

from .types import Rule


class ParseState:
    """An immutable view of the parser's position within a grammar.

    Iterating a ``ParseState`` yields the rules that may match next. Calling it (or
    calling :meth:`add`) with more input returns a new ``ParseState``.
    """

    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: str) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[Rule]:
        yield from self.rules()

    def rules(self) -> Iterator[Rule]:
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = rule.to_json()
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input) -> "ParseState":
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
        return f"ParseState({[rule for rule in self.rules()]})"
