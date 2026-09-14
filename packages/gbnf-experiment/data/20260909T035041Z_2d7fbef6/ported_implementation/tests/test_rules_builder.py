"""Tests for the flat rule definitions produced before the graph is built."""

import pytest

from gbnf import GrammarParseError
from gbnf.grammar_parser import build_rule_stack
from gbnf.rules_builder import InternalRuleType as T
from gbnf.rules_builder import RulesBuilder
from gbnf.rules_builder.parse_char import parse_char
from gbnf.rules_builder.parse_name import parse_name
from gbnf.rules_builder.parse_space import parse_space


def defs(rule):
    return [(d.type, getattr(d, "value", None)) for d in rule]


class TestRulesBuilder:
    def test_single_literal(self):
        builder = RulesBuilder('root ::= "ab"')
        assert defs(builder.rules[0]) == [
            (T.CHAR, [ord("a")]),
            (T.CHAR, [ord("b")]),
            (T.END, None),
        ]

    def test_alternates(self):
        builder = RulesBuilder('root ::= "a" | "b"')
        assert defs(builder.rules[0]) == [
            (T.CHAR, [ord("a")]),
            (T.ALT, None),
            (T.CHAR, [ord("b")]),
            (T.END, None),
        ]

    def test_character_range(self):
        builder = RulesBuilder("root ::= [a-z]")
        assert defs(builder.rules[0]) == [
            (T.CHAR, [ord("a")]),
            (T.CHAR_RNG_UPPER, ord("z")),
            (T.END, None),
        ]

    def test_negated_character_range(self):
        builder = RulesBuilder("root ::= [^a-z]")
        assert defs(builder.rules[0]) == [
            (T.CHAR_NOT, [ord("a")]),
            (T.CHAR_RNG_UPPER, ord("z")),
            (T.END, None),
        ]

    def test_character_alternates(self):
        builder = RulesBuilder("root ::= [abc]")
        assert defs(builder.rules[0]) == [
            (T.CHAR, [ord("a")]),
            (T.CHAR_ALT, ord("b")),
            (T.CHAR_ALT, ord("c")),
            (T.END, None),
        ]

    def test_reference(self):
        builder = RulesBuilder('root ::= foo\nfoo ::= "a"')
        assert defs(builder.rules[0]) == [(T.RULE_REF, 1), (T.END, None)]
        assert defs(builder.rules[1]) == [(T.CHAR, [ord("a")]), (T.END, None)]

    def test_symbol_ids_are_assigned_in_order_of_appearance(self):
        builder = RulesBuilder('root ::= foo bar\nfoo ::= "a"\nbar ::= "b"')
        assert list(builder.symbol_ids) == [("root", 0), ("foo", 1), ("bar", 2)]

    def test_quantifiers_generate_sub_rules(self):
        builder = RulesBuilder('root ::= "a"*')
        assert list(builder.symbol_ids) == [("root", 0), ("root_1", 1)]
        assert defs(builder.rules[0]) == [(T.RULE_REF, 1), (T.END, None)]
        assert defs(builder.rules[1]) == [
            (T.CHAR, [ord("a")]),
            (T.RULE_REF, 1),
            (T.ALT, None),
            (T.END, None),
        ]

    def test_plus_repeats_the_preceding_item(self):
        builder = RulesBuilder('root ::= "a"+')
        assert defs(builder.rules[1]) == [
            (T.CHAR, [ord("a")]),
            (T.RULE_REF, 1),
            (T.ALT, None),
            (T.CHAR, [ord("a")]),
            (T.END, None),
        ]

    def test_optional_does_not_self_reference(self):
        builder = RulesBuilder('root ::= "a"?')
        assert defs(builder.rules[1]) == [
            (T.CHAR, [ord("a")]),
            (T.ALT, None),
            (T.END, None),
        ]

    def test_groups_generate_sub_rules(self):
        builder = RulesBuilder('root ::= ("a" | "b")')
        assert list(builder.symbol_ids) == [("root", 0), ("root_1", 1)]
        assert defs(builder.rules[1]) == [
            (T.CHAR, [ord("a")]),
            (T.ALT, None),
            (T.CHAR, [ord("b")]),
            (T.END, None),
        ]

    def test_a_time_limit_is_enforced(self):
        with pytest.raises(GrammarParseError, match="duration of 0 exceeded"):
            RulesBuilder('root ::= "aaaaaaaaaaaaaaaaaaaa" | "b"', limit=0)


class TestBuildRuleStack:
    def test_splits_alternates_into_paths(self):
        builder = RulesBuilder('root ::= "a" | "b"')
        stack = build_rule_stack(builder.rules[0])
        assert len(stack) == 2
        assert [r.type.value for r in stack[0]] == ["char", "end"]
        assert [r.type.value for r in stack[1]] == ["char", "end"]

    def test_folds_range_upper_bounds_into_the_previous_value(self):
        builder = RulesBuilder("root ::= [a-z]")
        (path,) = build_rule_stack(builder.rules[0])
        assert path[0].value == [[ord("a"), ord("z")]]

    def test_folds_character_alternates(self):
        builder = RulesBuilder("root ::= [a-c0-9x]")
        (path,) = build_rule_stack(builder.rules[0])
        assert path[0].value == [[ord("a"), ord("c")], [ord("0"), ord("9")], ord("x")]

    def test_always_terminates_with_an_end_rule(self):
        builder = RulesBuilder('root ::= "a"')
        (path,) = build_rule_stack(builder.rules[0])
        assert path[-1].type.value == "end"


class TestParseHelpers:
    def test_parse_space_skips_spaces_and_tabs(self):
        assert parse_space("  \ta", 0, False) == 3

    def test_parse_space_stops_at_a_newline_unless_allowed(self):
        assert parse_space(" \n a", 0, False) == 1
        assert parse_space(" \n a", 0, True) == 3

    def test_parse_space_skips_comments(self):
        assert parse_space("# comment\na", 0, True) == 10

    def test_parse_name_reads_letters_and_hyphens(self):
        assert parse_name("foo-bar ::=", 0) == "foo-bar"

    def test_parse_name_requires_a_name(self):
        with pytest.raises(GrammarParseError, match="Failed to find a valid name"):
            parse_name("123", 0)

    @pytest.mark.parametrize(
        ("src", "expected"),
        [
            ("a", (ord("a"), 1)),
            ("\\n", (ord("\n"), 2)),
            ("\\t", (ord("\t"), 2)),
            ("\\r", (ord("\r"), 2)),
            ("\\x41", (0x41, 4)),
            ("\\u0041", (0x41, 6)),
            ("\\U0001F600", (0x1F600, 10)),
            ('\\"', (ord('"'), 2)),
            ("\\\\", (ord("\\"), 2)),
        ],
    )
    def test_parse_char(self, src, expected):
        assert parse_char(src, 0) == expected

    def test_parse_char_rejects_unknown_escapes(self):
        with pytest.raises(GrammarParseError, match="Unknown escape"):
            parse_char("\\q", 0)

    def test_parse_char_rejects_the_end_of_input(self):
        with pytest.raises(GrammarParseError, match="Unexpected end of grammar input"):
            parse_char("", 0)
