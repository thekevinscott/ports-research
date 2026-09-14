from typing import Iterator, Set

from .get_serialized_rule_key import get_serialized_rule_key


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: str) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator:
        return self.rules()

    def rules(self) -> Iterator:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input: str) -> "ParseState":
        pointers = self._graph.add(input, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, input: str) -> "ParseState":
        return self.add(input)

    def __bool__(self) -> bool:
        return True

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
