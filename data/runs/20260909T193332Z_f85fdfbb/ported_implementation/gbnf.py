from __future__ import annotations

from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder.rules_builder import RulesBuilder
from .utils.errors.grammar_parse_error import GrammarParseError
from .utils.utf16 import to_utf16_units


def GBNF(input, initial_string="") -> ParseState:
    """Parse a GBNF grammar and return the state of the parse.

    ``input`` is the grammar, either as a string or as anything that stringifies
    to one. ``initial_string`` is an optional prefix to consume immediately.
    """
    grammar = to_utf16_units(input if isinstance(input, str) else str(input))
    builder = RulesBuilder(grammar)
    rules, symbol_ids = builder.rules, builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    if symbol_ids.get("root") is None:
        raise GrammarParseError(
            grammar,
            0,
            "Grammar does not contain a root symbol. Available symbols are: "
            f"{symbol_ids.keys()}",
        )
    root_id = symbol_ids.get("root")

    stacked_rules = [
        build_rule_stack(rule) if rule is not None else None for rule in rules
    ]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
