import json
from typing import TYPE_CHECKING, Iterator, Set

from .types import ResolvedRule, ValidInput, rule_to_dict

if TYPE_CHECKING:  # pragma: no cover
    from .graph import Graph, Pointers


class ParseState:
    """An immutable view of where a parse currently stands.

    Iterate it to see the rules that may come next; call ``add`` (or the state
    itself) with more input to get the next state.
    """

    def __init__(self, graph: 'Graph', pointers: 'Pointers'):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input_: ValidInput) -> 'ParseState':
        return self.add(input_)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule_to_dict(rule), separators=(',', ':'))
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input_: ValidInput) -> 'ParseState':
        pointers = self._graph.add(input_, self._pointers)
        return ParseState(self._graph, pointers)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    def __bool__(self) -> bool:
        # a state is always a valid object, even when it offers no further rules
        return True

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f'ParseState({[rule_to_dict(rule) for rule in self.rules()]})'
