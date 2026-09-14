import json
from typing import Iterator

from .grammar_graph_types import ResolvedRule
from .graph import Graph
from .pointers import Pointers


class ParseState:
    """An immutable snapshot of where a parse currently stands: the set of rules
    the grammar will accept next. Feeding it more input returns a new
    ``ParseState``.
    """

    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.to_dict())
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise ValueError("input text must be of type string")
        pointers = self._graph.add(text, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, text: str) -> "ParseState":
        return self.add(text)

    def __call__(self, text: str) -> "ParseState":
        return self.add(text)

    def __len__(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar
