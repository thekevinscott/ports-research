from __future__ import annotations

import json
from typing import Any, Generator, Iterator

from .pointers import Pointers


def _rule_key(rule: Any) -> str:
    return json.dumps([rule.type.value, getattr(rule, "value", None)])


class ParseState:
    def __init__(self, graph: Any, pointers: Pointers):
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator[Any]:
        yield from self.rules()

    def rules(self) -> Generator[Any, None, None]:
        rules = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = _rule_key(rule)
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
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self._graph.grammar
