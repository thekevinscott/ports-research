from __future__ import annotations

from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder.rules_builder import RulesBuilder
from .utils.errors.grammar_parse_error import GrammarParseError


def GBNF(input, initial_string="") -> ParseState:
    """Parse a GBNF grammar and return the :class:`ParseState` it starts in."""
    grammar = input if isinstance(input, str) else str(input)
    builder = RulesBuilder(grammar)
    rules, symbol_ids = builder.rules, builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    if symbol_ids.get("root") is None:
        raise GrammarParseError(
            grammar,
            0,
            "Grammar does not contain a root symbol. Available symbols are: "
            f"{list(symbol_ids.keys())}",
        )
    root_id = symbol_ids.get("root")

    # `rules` may be sparse while sub-rules are generated; holes are carried through,
    # exactly as `Array.prototype.map` does in the reference implementation.
    stacked_rules = [None if rule is None else build_rule_stack(rule) for rule in rules]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
