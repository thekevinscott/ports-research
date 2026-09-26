import json

from .grammar_graph.graph import Graph
from .grammar_graph.parse_state import ParseState
from .grammar_graph.types import ValidInput
from .grammar_parser.build_rule_stack import build_rule_stack
from .rules_builder.rules_builder import RulesBuilder
from .utils.errors.grammar_parse_error import GrammarParseError


def GBNF(input_: str, initial_string: ValidInput = "") -> ParseState:
    grammar = input_ if isinstance(input_, str) else str(input_)
    builder = RulesBuilder(grammar)
    rules, symbol_ids = builder.rules, builder.symbol_ids
    if len(rules) == 0:
        raise GrammarParseError(grammar, 0, "No rules were found")
    if not symbol_ids.has("root"):
        raise GrammarParseError(
            grammar,
            0,
            "Grammar does not contain a root symbol. Available symbols are: "
            f"{json.dumps(list(symbol_ids.keys()))}",
        )
    root_id = symbol_ids.get("root")

    stacked_rules = [build_rule_stack(rule) for rule in rules]
    graph = Graph(grammar, stacked_rules, root_id)
    return ParseState(graph, graph.add(initial_string))
