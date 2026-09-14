"""A library for parsing GBNF grammars.

Python port of the `gbnf` TypeScript package.

    >>> from gbnf import GBNF
    >>> state = GBNF('root ::= "foo"')
    >>> [rule.to_dict() for rule in state]
    [{'type': 'char', 'value': [102]}]
    >>> [rule.to_dict() for rule in state.add('foo')]
    [{'type': 'end'}]
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
    ValidInput,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

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
