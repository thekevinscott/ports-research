"""Port of ``src/grammar-graph/parse-state.ts``.

The JS original extends ``Function`` and wraps itself in a ``Proxy`` so the state
can be called directly; here that is simply ``__call__``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, List

from .types import ResolvedRule

if TYPE_CHECKING:  # pragma: no cover
    from .graph import Graph, Pointers


class ParseState:
    def __init__(self, graph: "Graph", pointers: "Pointers") -> None:
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: str) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        # dicts preserve insertion order, so this yields in pointer order
        seen: Dict[ResolvedRule, None] = {}
        for pointer in self._pointers:
            rule = pointer.rule
            if rule not in seen:
                seen[rule] = None
                yield rule

    def add(self, input: str) -> "ParseState":
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
        return f"ParseState([{', '.join(rules)}])"
