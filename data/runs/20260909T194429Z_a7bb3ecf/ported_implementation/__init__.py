"""A library for parsing GBNF grammars.

A Python port of the TypeScript reference implementation. The entry point is
``GBNF``, which parses a grammar and returns an iterable :class:`ParseState`.
"""

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range, isRange
from .grammar_graph.types import (
    Range,
    ResolvedRule as Rule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
)
from .rules_builder.types import InternalRuleType
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

__all__ = [
    'GBNF',
    'GrammarParseError',
    'InputParseError',
    'InternalRuleType',
    'ParseState',
    'Range',
    'Rule',
    'RuleChar',
    'RuleCharExclude',
    'RuleEnd',
    'RuleType',
    'is_range',
    'isRange',
]

default = GBNF
