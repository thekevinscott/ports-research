"""A library for parsing GBNF grammars.

Python port of the Javascript ``gbnf`` package (see ``reference_implementation/``).

    >>> from ported_implementation import GBNF
    >>> state = GBNF('root ::= "yes" | "no"')
    >>> [rule.value for rule in state]
    [[121], [110]]
"""

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range
from .grammar_graph.types import (
    Range,
    ResolvedRule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    ValidInput,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

# Aliases mirroring the reference's export names.
Rule = ResolvedRule
isRange = is_range
gbnf = GBNF

__all__ = [
    "GBNF",
    "gbnf",
    "ParseState",
    "Rule",
    "ResolvedRule",
    "RuleType",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "Range",
    "ValidInput",
    "is_range",
    "isRange",
    "GrammarParseError",
    "InputParseError",
]
