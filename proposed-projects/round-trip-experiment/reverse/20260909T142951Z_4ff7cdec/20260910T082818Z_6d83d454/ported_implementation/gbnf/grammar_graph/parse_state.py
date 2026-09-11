from typing import Any, Iterator, List, Set

from .get_serialized_rule_key import get_serialized_rule_key
from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator[Any]:
        yield from self.rules()

    def rules(self) -> Iterator[Any]:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = get_serialized_rule_key(rule)
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

    def __len__(self) -> int:
        return len(self._rules_list())

    def _rules_list(self) -> List[Any]:
        return list(self.rules())

    @property
    def size(self) -> int:
        return len(self._rules_list())

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f"ParseState({self._rules_list()!r})"
