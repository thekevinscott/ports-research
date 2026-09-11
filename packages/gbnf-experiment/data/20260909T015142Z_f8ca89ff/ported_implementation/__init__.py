"""A library for parsing GBNF grammars — a Python port of the TypeScript `gbnf` package.

    from ported_implementation import GBNF

    state = GBNF('root ::= "yes" | "no"')
    for rule in state:
        print(rule)

`ParseState` objects are immutable; feed them more input with `state.add(...)`
(or by calling the state directly) to get the next state.
"""

from .gbnf import GBNF
from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_graph.type_guards import is_range, isRange
from .grammar_graph.types import (
    Range,
    ResolvedRule,
    Rule,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    UnresolvedRule,
    ValidInput,
)
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder.rules_builder import RulesBuilder
from .rules_builder.types import InternalRuleDef, InternalRuleType
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.errors.input_parse_error import InputParseError

__all__ = [
    "GBNF",
    "ParseState",
    "RuleType",
    "Rule",
    "ResolvedRule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "Range",
    "UnresolvedRule",
    "ValidInput",
    "is_range",
    "isRange",
    "GrammarParseError",
    "InputParseError",
    # internals, exposed for parity with the reference implementation
    "Graph",
    "RulesBuilder",
    "InternalRuleType",
    "InternalRuleDef",
    "build_rule_stack",
]

default = GBNF
