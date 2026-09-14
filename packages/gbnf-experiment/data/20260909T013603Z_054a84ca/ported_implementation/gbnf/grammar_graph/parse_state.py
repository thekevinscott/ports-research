from __future__ import annotations

from typing import Dict, Iterator, List

from .types import Rule, ValidInput


class ParseState:
    """The rules that may come next, given the input consumed so far.

    Iterating a `ParseState` yields the currently valid rules; calling it (or
    calling `add`) with more input returns the next `ParseState`.
    """

    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> 'ParseState':
        return self.add(input)

    def __iter__(self) -> Iterator[Rule]:
        return self.rules()

    def rules(self) -> Iterator[Rule]:
        rules: Dict[str, None] = {}
        for pointer in self._pointers:
            rule = pointer.rule
            key = rule.serialize()
            if key not in rules:
                rules[key] = None
                yield rule

    def add(self, input: ValidInput) -> 'ParseState':
        pointers = self._graph.add(input, self._pointers)
        return ParseState(self._graph, pointers)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        rules: List[str] = [rule.serialize() for rule in self.rules()]
        return f'ParseState([{", ".join(rules)}])'
