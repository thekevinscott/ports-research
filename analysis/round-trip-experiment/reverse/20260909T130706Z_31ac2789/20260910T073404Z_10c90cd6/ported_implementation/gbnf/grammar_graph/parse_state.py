import json
from typing import Generator, Set

from .grammar_graph_types import ResolvedRule
from .graph import Graph
from .pointers import Pointers


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self.__graph__ = graph
        self.__pointers__ = pointers

    def __iter__(self) -> Generator[ResolvedRule, None, None]:
        yield from self.rules()

    def rules(self) -> Generator[ResolvedRule, None, None]:
        rules: Set[str] = set()
        for pointer in self.__pointers__:
            rule = pointer.rule
            key = json.dumps(rule.to_json())
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise ValueError("input text must be of type string")
        pointers = self.__graph__.add(text, self.__pointers__)
        return ParseState(self.__graph__, pointers)

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
        return self.__graph__.grammar

    @property
    def pointers(self) -> Pointers:
        return self.__pointers__

    @property
    def graph(self) -> Graph:
        return self.__graph__

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
