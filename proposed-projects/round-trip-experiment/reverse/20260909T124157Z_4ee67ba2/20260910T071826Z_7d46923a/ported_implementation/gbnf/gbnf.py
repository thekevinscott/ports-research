from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder import GrammarParseError, RulesBuilder


def GBNF(grammar: str, initial_string: str = "") -> ParseState:
    if not isinstance(grammar, str):
        raise Exception("grammar must be a string")

    if not isinstance(initial_string, str):
        raise Exception("input must be a string")

    rules_builder = RulesBuilder(grammar)
    rules = rules_builder.rules
    symbol_ids = rules_builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    root_id = symbol_ids.get("root")
    if root_id is None:
        raise GrammarParseError(
            grammar, 0, "Grammar does not contain a 'root' symbol"
        )

    stacked_rules = [build_rule_stack(rule) for rule in rules]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
