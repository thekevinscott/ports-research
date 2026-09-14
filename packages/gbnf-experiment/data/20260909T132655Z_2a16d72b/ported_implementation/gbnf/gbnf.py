import json

from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_graph.types import ValidInput
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder import RulesBuilder
from .utils.errors.grammar_parse_error import GrammarParseError


def GBNF(input: str, initial_string: ValidInput = "") -> ParseState:
    grammar = input if isinstance(input, str) else str(input)
    builder = RulesBuilder(grammar)
    rules, symbol_ids = builder.rules, builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    if symbol_ids.get_or_none("root") is None:
        available = json.dumps(list(symbol_ids.keys()))
        raise GrammarParseError(
            grammar,
            0,
            f"Grammar does not contain a root symbol. Available symbols are: {available}",
        )
    root_id = symbol_ids.get("root")

    stacked_rules = [build_rule_stack(rule) for rule in rules]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
