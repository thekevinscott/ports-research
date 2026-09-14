from .grammar_graph_types import RuleChar
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer
from .parse_state import ParseState


class MockGraph:
    grammar = "sample-grammar"

    def __init__(self):
        self.calls = []

    def add(self, input, pointers):
        self.calls.append((input, pointers))
        return pointers


def mock_pointers():
    return [
        GraphPointer(GraphNode(RuleChar([65]), GraphNodeMeta(1, 1, 1))),
    ]


def test_constructs_with_given_graph_and_pointers():
    parse_state = ParseState(MockGraph(), mock_pointers())
    assert isinstance(parse_state, ParseState)


def test_returns_unique_rules_from_pointers():
    parse_state = ParseState(MockGraph(), mock_pointers())
    rules = list(parse_state.rules())
    assert len(rules) == 1
    assert isinstance(rules[0], RuleChar)
    assert rules[0].value == [65]


def test_iterates_over_unique_rules_using_the_iterator_protocol():
    parse_state = ParseState(MockGraph(), mock_pointers())
    rules = list(parse_state)
    assert len(rules) == 1
    assert isinstance(rules[0], RuleChar)


def test_adds_new_input_and_returns_new_parse_state_with_updated_pointers():
    mock_graph = MockGraph()
    pointers = mock_pointers()
    parse_state = ParseState(mock_graph, pointers)
    new_state = parse_state.add("B")
    assert isinstance(new_state, ParseState)
    assert mock_graph.calls == [("B", pointers)]


def test_calling_the_state_is_the_same_as_adding():
    mock_graph = MockGraph()
    pointers = mock_pointers()
    parse_state = ParseState(mock_graph, pointers)
    assert isinstance(parse_state("B"), ParseState)
    assert mock_graph.calls == [("B", pointers)]


def test_adding_a_string_to_the_state_is_the_same_as_adding():
    mock_graph = MockGraph()
    pointers = mock_pointers()
    parse_state = ParseState(mock_graph, pointers)
    assert isinstance(parse_state + "B", ParseState)
    assert mock_graph.calls == [("B", pointers)]


def test_calculates_the_size_of_unique_rules_correctly():
    parse_state = ParseState(MockGraph(), mock_pointers())
    assert parse_state.size == 1


def test_provides_access_to_the_underlying_graph_grammar():
    parse_state = ParseState(MockGraph(), mock_pointers())
    assert parse_state.grammar == "sample-grammar"
