import json
from typing import Any, Generator, Iterator, Set


class ParseState:
    def __init__(self, graph: Any, pointers: Any):
        self.__graph = graph
        self.__pointers = pointers

    def __iter__(self) -> Iterator[Any]:
        return self.rules()

    def rules(self) -> Generator[Any, None, None]:
        rules: Set[str] = set()
        for pointer in self.__pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__)
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

    def __call__(self, text: str) -> "ParseState":
        return self.add(text)

    def __len__(self) -> int:
        return len(list(self.rules()))

    @property
    def size(self) -> int:
        return len(self)

    @property
    def grammar(self) -> str:
        return self.__graph.grammar
