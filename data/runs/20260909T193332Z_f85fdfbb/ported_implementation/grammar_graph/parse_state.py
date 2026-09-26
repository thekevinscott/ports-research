from __future__ import annotations

from typing import Iterator


class ParseState:
    """An immutable snapshot of the parse: the rules that may come next."""

    __slots__ = ("_graph", "_pointers")

    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input_: str) -> "ParseState":
        return self.add(input_)

    def __iter__(self) -> Iterator:
        yield from self.rules()

    def rules(self) -> Iterator:
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = rule.to_json()
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input_) -> "ParseState":
        pointers = self._graph.add(input_, self._pointers)
        return ParseState(self._graph, pointers)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ParseState({list(self.rules())!r})"
