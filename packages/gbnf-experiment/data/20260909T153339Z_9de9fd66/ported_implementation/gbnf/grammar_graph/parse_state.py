from typing import Iterator, List

from .get_serialized_rule_key import get_serialized_rule_key
from .types import Rule, ValidInput


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[Rule]:
        return self.rules()

    def rules(self) -> Iterator[Rule]:
        seen = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input: ValidInput) -> "ParseState":
        pointers = self._graph.add(input, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

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
        rules: List[Rule] = list(self.rules())
        return f"ParseState({rules!r})"
