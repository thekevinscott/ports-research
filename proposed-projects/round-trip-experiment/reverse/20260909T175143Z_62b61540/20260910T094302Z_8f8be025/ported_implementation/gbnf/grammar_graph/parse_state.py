import json
from typing import Iterator

from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator:
        yield from self.rules()

    def rules(self) -> Iterator:
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__, separators=(",", ":"))
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

    @property
    def size(self) -> int:
        return len([*self.rules()])

    @property
    def grammar(self) -> str:
        return self._graph.grammar
