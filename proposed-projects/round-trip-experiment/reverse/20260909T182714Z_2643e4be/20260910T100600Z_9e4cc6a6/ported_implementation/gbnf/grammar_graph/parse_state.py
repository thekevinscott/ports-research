from __future__ import annotations

import json
from typing import Iterator, Set

from .grammar_graph_types import ResolvedRule
from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers) -> None:
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        rules: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__)
            if key not in rules:
                rules.add(key)
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

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def pointers(self) -> Pointers:
        return self._pointers
