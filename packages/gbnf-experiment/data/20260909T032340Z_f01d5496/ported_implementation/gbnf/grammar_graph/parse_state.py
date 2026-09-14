import json
from typing import Iterator, Set

from .types import ValidInput


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input_: ValidInput) -> "ParseState":
        return self.add(input_)

    def __iter__(self) -> Iterator:
        return self.rules()

    def __add__(self, input_: ValidInput) -> "ParseState":
        return self.add(input_)

    def rules(self) -> Iterator:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__, sort_keys=True)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input_: ValidInput) -> "ParseState":
        pointers = self._graph.add(input_, self._pointers)
        return ParseState(self._graph, pointers)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
