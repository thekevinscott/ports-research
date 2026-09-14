"""A library for parsing GBNF grammars.

Python port of the reference TypeScript implementation.
"""

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

Rule = (RuleChar, RuleCharExclude, RuleEnd)

__all__ = [
    'GBNF',
    'GrammarParseError',
    'InputParseError',
    'ParseState',
    'Range',
    'Rule',
    'RuleChar',
    'RuleCharExclude',
    'RuleEnd',
    'RuleType',
    'ValidInput',
    'is_range',
]
