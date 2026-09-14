"""A library for parsing GBNF grammars.

A Python port of the `gbnf` JavaScript package.

    from ported_implementation import GBNF

    state = GBNF('root ::= "yes" | "no"')
    for rule in state:
        print(rule)

`state` is immutable; call `state.add("y")` (or `state("y")`) to parse a token
and get the next state.
"""

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range
from .grammar_graph.types import (
    Range,
    Rule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

# camelCase alias, mirroring the reference API.
isRange = is_range

__all__ = [
    "GBNF",
    "ParseState",
    "Rule",
    "RuleType",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "Range",
    "is_range",
    "isRange",
    "GrammarParseError",
    "InputParseError",
]
