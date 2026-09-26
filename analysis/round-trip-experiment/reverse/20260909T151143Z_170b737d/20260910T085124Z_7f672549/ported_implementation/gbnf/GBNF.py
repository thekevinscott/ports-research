from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder import GrammarParseError, RulesBuilder


def GBNF(grammar: str, initial_string: str = "") -> ParseState:
    if not isinstance(grammar, str):
        raise ValueError("grammar must be a string")

    if not isinstance(initial_string, str):
        raise ValueError("input must be a string")

    rules_builder = RulesBuilder(grammar)
    rules = rules_builder.rules
    symbol_ids = rules_builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    # Looking up a missing symbol raises rather than returning None, so a
    # grammar without a `root` rule surfaces as a KeyError.
    root_id = symbol_ids["root"]

    stacked_rules = [build_rule_stack(rule) for rule in rules]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
