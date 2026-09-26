"""A library for parsing GBNF grammars.

A Python port of the `gbnf` TypeScript package.

    >>> from ported_implementation import GBNF
    >>> state = GBNF('root ::= "yes" | "no"')
    >>> [rule.value for rule in state]
    [[121], [110]]
    >>> state = state.add('y')
    >>> [rule.value for rule in state]
    [[101]]
"""

from .gbnf import GBNF
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range
from .grammar_graph.types import (
    Range,
    ResolvedRule,
    ResolvedRule as Rule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    ValidInput,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

# `export { GBNF as default }`
default = GBNF
# JS-name alias for parity with the reference implementation.
isRange = is_range

__all__ = [
    'GBNF',
    'GrammarParseError',
    'InputParseError',
    'ParseState',
    'Range',
    'ResolvedRule',
    'Rule',
    'RuleChar',
    'RuleCharExclude',
    'RuleEnd',
    'RuleType',
    'ValidInput',
    'default',
    'isRange',
    'is_range',
]
