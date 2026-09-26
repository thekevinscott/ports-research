from typing import TYPE_CHECKING, Iterator, List

from .types import ResolvedRule, ValidInput

if TYPE_CHECKING:
    from .graph import Graph, Pointers


class ParseState:
    def __init__(self, graph: "Graph", pointers: "Pointers"):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen = set()
        for pointer in self._pointers:
            rule = pointer.rule
            if rule not in seen:
                seen.add(rule)
                yield rule

    def add(self, input: ValidInput) -> "ParseState":
        pointers = self._graph.add(input, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        rules: List[ResolvedRule] = list(self.rules())
        return f"ParseState({rules!r})"
