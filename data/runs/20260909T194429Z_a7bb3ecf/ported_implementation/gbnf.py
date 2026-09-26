from __future__ import annotations

import json
from typing import List, Optional

from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_graph.types import UnresolvedRule, ValidInput
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder import RulesBuilder
from .utils.errors.grammar_parse_error import GrammarParseError


def GBNF(input: str, initial_string: ValidInput = '') -> ParseState:
    grammar = input if isinstance(input, str) else str(input)
    builder = RulesBuilder(grammar)
    rules, symbol_ids = builder.rules, builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, 'No rules were found')
    if symbol_ids.get('root') is None:
        raise GrammarParseError(
            grammar,
            0,
            'Grammar does not contain a root symbol. '
            f'Available symbols are: {json.dumps({})}',
        )
    root_id = symbol_ids.get('root')

    stacked_rules: List[Optional[List[List[UnresolvedRule]]]] = [
        build_rule_stack(rule) if rule is not None else None for rule in rules
    ]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
