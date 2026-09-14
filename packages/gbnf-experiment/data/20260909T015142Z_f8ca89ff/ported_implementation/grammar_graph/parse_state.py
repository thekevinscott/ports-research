from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, List, Set

from .types import Pointers, ResolvedRule, ValidInput

if TYPE_CHECKING:  # pragma: no cover
    from .graph import Graph

__all__ = ["ParseState"]


class ParseState:
    """An immutable view of the parser's position within a grammar.

    Iterate it to see the rules that may come next; call it (or use `add`) with
    more input to get the next state.
    """

    def __init__(self, graph: "Graph", pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = rule.to_json()
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
        rules: List[str] = [rule.to_json() for rule in self.rules()]
        return f"ParseState([{', '.join(rules)}])"
