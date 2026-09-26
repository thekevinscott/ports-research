import json
from typing import Generator, Set

from .grammar_graph_types import ResolvedRule
from .graph import Graph
from .pointers import Pointers


def serialize_rule(rule: ResolvedRule) -> str:
    return json.dumps(
        {
            "type": rule.type,
            "value": getattr(rule, "value", None),
        }
    )


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Generator[ResolvedRule, None, None]:
        yield from self.rules()

    def rules(self) -> Generator[ResolvedRule, None, None]:
        rules: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = serialize_rule(rule)
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise TypeError("input text must be of type string")
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
