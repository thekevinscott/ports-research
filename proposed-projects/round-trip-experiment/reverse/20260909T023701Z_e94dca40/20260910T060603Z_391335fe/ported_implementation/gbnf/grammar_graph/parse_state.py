from __future__ import annotations

import json
from typing import Iterator


class ParseState:
    def __init__(self, graph, pointers) -> None:
        self._graph = graph
        self._pointers = pointers

    def __iter__(self) -> Iterator:
        return self.rules()

    def rules(self) -> Iterator:
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key_parts = {"type": str(rule.type)}
            if hasattr(rule, "value"):
                key_parts["value"] = rule.value
            key = json.dumps(key_parts)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, text: str) -> ParseState:
        if not isinstance(text, str):
            raise ValueError("input text must be of type string")
        pointers = self._graph.add(text, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, text: str) -> ParseState:
        return self.add(text)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self._graph.grammar
