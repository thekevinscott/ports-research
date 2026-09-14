"""A library for parsing GBNF grammars.

    from gbnf import GBNF

    state = GBNF('root ::= "yes" | "no"')
    for rule in state:
        print(rule)

States are immutable; ``state.add(token)`` returns the next state.
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
    rule_to_dict,
)
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

Rule = ResolvedRule

__all__ = [
    'GBNF',
    'ParseState',
    'is_range',
    'Range',
    'Rule',
    'ResolvedRule',
    'RuleChar',
    'RuleCharExclude',
    'RuleEnd',
    'RuleType',
    'ValidInput',
    'rule_to_dict',
    'GrammarParseError',
    'InputParseError',
]
