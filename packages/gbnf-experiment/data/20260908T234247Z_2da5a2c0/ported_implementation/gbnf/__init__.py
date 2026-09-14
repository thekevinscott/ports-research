"""A library for parsing GBNF grammars — a Python port of the TypeScript `gbnf` package."""

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range
from .grammar_graph.types import (
    Range,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    ValidInput,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

# `ResolvedRule` is exported as `Rule`, matching the TypeScript entry point.
from .grammar_graph.types import ResolvedRule as Rule

__all__ = [
    "GBNF",
    "is_range",
    "RuleType",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "Range",
    "ValidInput",
    "ParseState",
    "InputParseError",
    "GrammarParseError",
]
