import json
from typing import Generator

from .grammar_graph_types import ResolvedRule


class ParseState:
    def __init__(self, graph, pointers):
        self.__graph__ = graph
        self.__pointers__ = pointers

    def __iter__(self) -> Generator[ResolvedRule, None, None]:
        yield from self.rules()

    def rules(self) -> Generator[ResolvedRule, None, None]:
        rules = set()
        for pointer in self.__pointers__:
            rule = pointer.rule
            key = json.dumps(rule.__dict__)
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

    @property
    def grammar(self) -> str:
        return self.__graph__.grammar

    def __repr__(self) -> str:
        return f"<ParseState {list(self.rules())}>"
