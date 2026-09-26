"""The user facing view of a position in the grammar."""

import json
from typing import Any, Generator, Set

from .graph import Graph
from .pointers import Pointers


def get_rule_key(rule: Any) -> str:
    key = {"type": rule.type}
    if hasattr(rule, "value"):
        key["value"] = rule.value
    return json.dumps(key, separators=(",", ":"))


class ParseState:
    def __init__(self, graph: Graph, pointers: Pointers):
        self.graph = graph
        self.pointers = pointers

    def __iter__(self) -> Generator[Any, None, None]:
        yield from self.rules()

    def rules(self) -> Generator[Any, None, None]:
        rules: Set[str] = set()
        for pointer in self.pointers:
            rule = pointer.rule
            key = get_rule_key(rule)
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, text: str) -> "ParseState":
        if not isinstance(text, str):
            raise ValueError("input text must be of type string")
        pointers = self.graph.add(text, self.pointers)
        return ParseState(self.graph, pointers)

    def __add__(self, text: str) -> "ParseState":
        return self.add(text)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self.graph.grammar

    def __repr__(self) -> str:
        return f"ParseState(rules={list(self.rules())!r})"
