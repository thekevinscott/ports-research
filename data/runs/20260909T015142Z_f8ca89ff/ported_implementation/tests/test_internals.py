"""Tests for the internal modules, mirroring the reference implementation's layout."""
import pytest

from ported_implementation.grammar_graph.generic_set import GenericSet
from ported_implementation.grammar_graph.get_input_as_code_points import (
    get_input_as_code_points,
)
from ported_implementation.grammar_graph.get_serialized_rule_key import (
    get_serialized_rule_key,
)
from ported_implementation.grammar_graph.graph import Graph
from ported_implementation.grammar_graph.rule_ref import RuleRef
from ported_implementation.grammar_graph.type_guards import (
    is_range,
    is_rule,
    is_rule_char,
    is_rule_char_excluded,
    is_rule_end,
    is_rule_ref,
    is_rule_type,
)
from ported_implementation.grammar_graph.types import (
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
)
from ported_implementation.grammar_parser.build_rule_stack import build_rule_stack
from ported_implementation.rules_builder.is_word_char import is_word_char
from ported_implementation.rules_builder.parse_char import parse_char
from ported_implementation.rules_builder.parse_name import parse_name
from ported_implementation.rules_builder.parse_space import parse_space
from ported_implementation.rules_builder.rules_builder import RulesBuilder
from ported_implementation.rules_builder.symbol_ids import SymbolIds, SymbolIdsKeyError
from ported_implementation.rules_builder.types import InternalRuleType
from ported_implementation.utils.errors.grammar_parse_error import GrammarParseError
from ported_implementation.utils.is_point_in_range import is_point_in_range


class TestParseChar:
    @pytest.mark.parametrize(
        "src,expected",
        [
            ("a", (97, 1)),
            (r"\n", (10, 2)),
            (r"\r", (13, 2)),
            (r"\t", (9, 2)),
            (r"\\", (92, 2)),
            (r"\"", (34, 2)),
            (r"\[", (91, 2)),
            (r"\]", (93, 2)),
            (r"\x41", (65, 4)),
            ("é", (0xE9, 1)),
            ("\\u00e9", (0xE9, 6)),
            (r"\U0001F600", (0x1F600, 10)),
        ],
    )
    def test_parses(self, src, expected):
        assert parse_char(src, 0) == expected

    def test_unknown_escape(self):
        with pytest.raises(GrammarParseError, match="Unknown escape"):
            parse_char(r"\q", 0)

    def test_end_of_input(self):
        with pytest.raises(GrammarParseError, match="Unexpected end of grammar input"):
            parse_char("", 0)


class TestParseName:
    @pytest.mark.parametrize(
        "grammar,pos,expected",
        [
            ("root ::= x", 0, "root"),
            ("foo-bar ::= x", 0, "foo-bar"),
            ("  abc", 2, "abc"),
            ("MixedCase", 0, "MixedCase"),
        ],
    )
    def test_parses(self, grammar, pos, expected):
        assert parse_name(grammar, pos) == expected

    def test_requires_a_name(self):
        with pytest.raises(GrammarParseError, match="Failed to find a valid name"):
            parse_name("::= x", 0)

    @pytest.mark.parametrize("grammar", ["foo1", "foo_bar"])
    def test_rejects_invalid_next_char(self, grammar):
        with pytest.raises(GrammarParseError, match="Invalid character"):
            parse_name(grammar, 0)


class TestParseSpace:
    @pytest.mark.parametrize(
        "src,pos,newline_ok,expected",
        [
            ("   a", 0, False, 3),
            ("\t\t a", 0, False, 3),
            ("\n\n a", 0, False, 0),
            ("\n\n a", 0, True, 3),
            ("# comment\na", 0, False, 9),
            ("# comment\na", 0, True, 10),
            ("abc", 0, True, 0),
            ("", 0, True, 0),
        ],
    )
    def test_advances_past_whitespace(self, src, pos, newline_ok, expected):
        assert parse_space(src, pos, newline_ok) == expected


@pytest.mark.parametrize(
    "char,expected",
    [("a", True), ("Z", True), ("1", False), ("-", False), (" ", False), ("", False)],
)
def test_is_word_char(char, expected):
    assert is_word_char(char) is expected


class TestSymbolIds:
    def test_set_and_get(self):
        symbol_ids = SymbolIds()
        symbol_ids.set("root", 0, 4)
        symbol_ids.set("foo", 1, 12)
        assert symbol_ids.size == 2
        assert len(symbol_ids) == 2
        assert symbol_ids.get("root") == 0
        assert symbol_ids.reverse_get(1) == "foo"
        assert symbol_ids.get_pos("foo") == 12
        assert symbol_ids.has("root")
        assert "foo" in symbol_ids
        assert symbol_ids.keys() == ["root", "foo"]
        assert list(symbol_ids) == [("root", 0), ("foo", 1)]

    def test_missing_key(self):
        symbol_ids = SymbolIds()
        with pytest.raises(SymbolIdsKeyError) as excinfo:
            symbol_ids.get("root")
        assert str(excinfo.value) == "SymbolIds does not contain key: root"
        # it is still an ordinary KeyError
        assert isinstance(excinfo.value, KeyError)

    def test_missing_value(self):
        with pytest.raises(SymbolIdsKeyError, match="does not contain value"):
            SymbolIds().reverse_get(3)


class TestRulesBuilder:
    def test_builds_linear_rules(self):
        builder = RulesBuilder('root ::= "a" | [b-d]')
        assert [[r.to_dict() for r in rule] for rule in builder.rules] == [
            [
                {"type": "CHAR", "value": [97]},
                {"type": "ALT"},
                {"type": "CHAR", "value": [98]},
                {"type": "CHAR_RNG_UPPER", "value": 100},
                {"type": "END"},
            ]
        ]

    def test_records_symbol_ids(self):
        builder = RulesBuilder('root ::= foo\nfoo ::= "a"')
        assert list(builder.symbol_ids) == [("root", 0), ("foo", 1)]
        assert builder.symbolIds is builder.symbol_ids

    def test_generates_sub_rules_for_quantifiers(self):
        builder = RulesBuilder('root ::= "a"*')
        assert len(builder.rules) == 2
        assert builder.rules[1][-1].type == InternalRuleType.END

    def test_rejects_undefined_rules(self):
        with pytest.raises(GrammarParseError, match="Undefined rule identifier"):
            RulesBuilder("root ::= missing")

    def test_time_limit(self):
        with pytest.raises(GrammarParseError, match="duration of 0 exceeded"):
            RulesBuilder('root ::= "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa"', 0)


class TestBuildRuleStack:
    def test_splits_on_alternates_and_collapses_ranges(self):
        builder = RulesBuilder('root ::= "ab" | [c-e]')
        stack = build_rule_stack(builder.rules[0])
        assert [[r.to_dict() for r in path] for path in stack] == [
            [
                {"type": "char", "value": [97]},
                {"type": "char", "value": [98]},
                {"type": "end"},
            ],
            [{"type": "char", "value": [[99, 101]]}, {"type": "end"}],
        ]

    def test_emits_rule_refs(self):
        builder = RulesBuilder('root ::= foo\nfoo ::= "a"')
        stack = build_rule_stack(builder.rules[0])
        assert isinstance(stack[0][0], RuleRef)
        assert stack[0][0].value == 1

    def test_collapses_char_alts(self):
        builder = RulesBuilder("root ::= [abc]")
        stack = build_rule_stack(builder.rules[0])
        assert stack[0][0].to_dict() == {"type": "char", "value": [97, 98, 99]}


class TestTypeGuards:
    def test_rule_guards(self):
        char = RuleChar([97])
        excluded = RuleCharExclude([97])
        end = RuleEnd()
        ref = RuleRef(0)

        assert is_rule_char(char) and not is_rule_char(end)
        assert is_rule_char_excluded(excluded) and not is_rule_char_excluded(char)
        assert is_rule_end(end) and not is_rule_end(char)
        assert is_rule_ref(ref) and not is_rule_ref(char)
        assert is_rule(char) and is_rule(end) and not is_rule(ref)
        assert is_rule_type(RuleType.CHAR) and is_rule_type("char")
        assert not is_rule_type("nope") and not is_rule_type(None)

    @pytest.mark.parametrize(
        "value,expected",
        [([1, 2], True), ((1, 2), True), ([1], False), ([1, 2, 3], False),
         (1, False), (None, False), (["a", "b"], False)],
    )
    def test_is_range(self, value, expected):
        assert is_range(value) is expected


@pytest.mark.parametrize(
    "point,rng,expected",
    [(5, [1, 10], True), (1, [1, 10], True), (10, [1, 10], True), (0, [1, 10], False),
     (11, [1, 10], False)],
)
def test_is_point_in_range(point, rng, expected):
    assert is_point_in_range(point, rng) is expected


@pytest.mark.parametrize(
    "src,expected",
    [("ab", [97, 98]), (97, [97]), ([97, 98], [97, 98]), ("", []), ("é", [0xE9])],
)
def test_get_input_as_code_points(src, expected):
    assert get_input_as_code_points(src) == expected


class TestGetSerializedRuleKey:
    def test_keys_are_distinct_per_rule(self):
        assert get_serialized_rule_key(RuleEnd()) == "0"
        assert get_serialized_rule_key(RuleChar([97])) == "1-[97]"
        assert get_serialized_rule_key(RuleChar([[97, 122]])) == "1-[[97,122]]"
        assert get_serialized_rule_key(RuleCharExclude([97])) == "2-[97]"
        assert get_serialized_rule_key(RuleRef(4)) == "3-4"

    def test_rejects_unknown_rules(self):
        with pytest.raises(Exception, match="Unknown rule type"):
            get_serialized_rule_key(object())


class TestGenericSet:
    def test_dedupes_on_key(self):
        gs = GenericSet(lambda item: item["id"])
        first = {"id": 1}
        duplicate = {"id": 1}
        second = {"id": 2}
        gs.add(first)
        gs.add(duplicate)
        gs.add(second)
        assert gs.size == 2
        assert list(gs) == [first, second]
        assert gs.has(first)
        assert not gs.has(duplicate)  # membership is by identity
        assert gs.get(duplicate) is first

    def test_delete(self):
        gs = GenericSet(lambda item: item["id"])
        item = {"id": 1}
        gs.add(item)
        gs.delete(item)
        assert gs.size == 0
        with pytest.raises(Exception, match="Could not get ref"):
            gs.delete(item)


class TestGraph:
    def test_print(self):
        grammar = 'root ::= "ab"'
        builder = RulesBuilder(grammar)
        graph = Graph(grammar, [build_rule_stack(r) for r in builder.rules], 0)
        assert graph.print(colors=False) == "\n{0,0,0}[a]-> {0,0,1}[b]-> {0,0,2}end"

    def test_print_with_colors_contains_escape_codes(self):
        grammar = 'root ::= "a"'
        builder = RulesBuilder(grammar)
        graph = Graph(grammar, [build_rule_stack(r) for r in builder.rules], 0)
        assert "\x1b[" in graph.print(colors=True)

    def test_unknown_root(self):
        grammar = 'root ::= "a"'
        builder = RulesBuilder(grammar)
        with pytest.raises(Exception, match="Root node not found"):
            Graph(grammar, [build_rule_stack(r) for r in builder.rules], 99)


class TestRuleRef:
    def test_nodes_must_be_set(self):
        with pytest.raises(Exception, match="Nodes are not set"):
            RuleRef(0).nodes

    def test_nodes_round_trip(self):
        ref = RuleRef(0)
        ref.nodes = []
        assert ref.nodes == []
        assert repr(ref) == "RuleRef(0)"
