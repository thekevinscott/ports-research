import json
from typing import Iterator, List, Set

from .grammar_graph_types import ResolvedRule
from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator[ResolvedRule]:
        return self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        rules: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.to_json())
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

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    def __bool__(self) -> bool:
        return True

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        rules: List[ResolvedRule] = list(self.rules())
        return f"ParseState({rules!r})"
