import json
from typing import TYPE_CHECKING, Iterator, Set

if TYPE_CHECKING:
    from .grammar_graph_types import ResolvedRule
    from .graph import Graph
    from .pointers import Pointers


def get_rule_key(rule: "ResolvedRule") -> str:
    key = {"type": rule.type}
    if hasattr(rule, "value"):
        key["value"] = rule.value
    return json.dumps(key)


class ParseState:
    def __init__(self, graph: "Graph", pointers: "Pointers"):
        self.__graph = graph
        self.__pointers = pointers

    def __iter__(self) -> Iterator["ResolvedRule"]:
        yield from self.rules()

    def rules(self) -> Iterator["ResolvedRule"]:
        rules: Set[str] = set()
        for pointer in self.__pointers:
            rule = pointer.rule
            key = get_rule_key(rule)
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise Exception("input text must be of type string")
        pointers = self.__graph.add(text, self.__pointers)
        return ParseState(self.__graph, pointers)

    def __add__(self, text: str) -> "ParseState":
        return self.add(text)

    def __len__(self) -> int:
        return len(list(self.rules()))

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self.__graph.grammar
