import json
from typing import Iterator

from .grammar_graph_types import ResolvedRule


def _serialize(rule) -> str:
    return json.dumps(rule.__dict__)


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def rules(self) -> Iterator[ResolvedRule]:
        seen = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = _serialize(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def __iter__(self) -> Iterator[ResolvedRule]:
        return self.rules()

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise TypeError("input text must be of type string")
        return ParseState(self._graph, self._graph.add(text, self._pointers))

    def __add__(self, text: str) -> "ParseState":
        return self.add(text)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar
