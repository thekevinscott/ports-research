"""Port of ``src/grammar-graph/parse-state.ts``."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterator, List, Set

from .type_guards import is_rule_end
from .types import ResolvedRule, ValidInput

if TYPE_CHECKING:  # pragma: no cover
    from .generic_set import GenericSet
    from .graph import Graph


def _serialize_rule(rule: Any) -> str:
    """``JSON.stringify(rule)`` for the deduplication key used by ``rules()``."""
    if is_rule_end(rule):
        return json.dumps({"type": rule.type.value}, separators=(",", ":"))
    return json.dumps(
        {"type": rule.type.value, "value": rule.value}, separators=(",", ":")
    )


class ParseState:
    """The immutable parse state returned by :func:`GBNF`.

    Calling an instance (``state("abc")``) is equivalent to ``state.add("abc")``,
    mirroring the callable ``ParseState`` of the reference implementation.
    """

    def __init__(self, graph: "Graph", pointers: "GenericSet"):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input: ValidInput) -> "ParseState":
        return self.add(input)

    def __iter__(self) -> Iterator[ResolvedRule]:
        yield from self.rules()

    def rules(self) -> Iterator[ResolvedRule]:
        seen: Set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = _serialize_rule(rule)
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input: ValidInput) -> "ParseState":
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

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        rules: List[ResolvedRule] = list(self.rules())
        return f"ParseState({rules!r})"
