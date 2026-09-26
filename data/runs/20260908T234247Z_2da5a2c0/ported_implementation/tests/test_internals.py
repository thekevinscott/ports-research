"""Tests for the individual ported modules, mirroring the reference's file layout."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gbnf.grammar_graph.generic_set import GenericSet  # noqa: E402
from gbnf.grammar_graph.get_input_as_code_points import get_input_as_code_points  # noqa: E402
from gbnf.grammar_graph.get_serialized_rule_key import get_serialized_rule_key  # noqa: E402
from gbnf.grammar_graph.rule_ref import RuleRef  # noqa: E402
from gbnf.grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd  # noqa: E402
from gbnf.grammar_parser.build_rule_stack import build_rule_stack  # noqa: E402
from gbnf.rules_builder import RulesBuilder  # noqa: E402
from gbnf.rules_builder.is_word_char import is_word_char  # noqa: E402
from gbnf.rules_builder.parse_char import parse_char  # noqa: E402
from gbnf.rules_builder.parse_name import (  # noqa: E402
    GET_INVALID_CHAR_ERROR,
    PARSE_NAME_ERROR,
    parse_name,
)
from gbnf.rules_builder.parse_space import parse_space  # noqa: E402
from gbnf.rules_builder.symbol_ids import SymbolIds  # noqa: E402
from gbnf.rules_builder.types import InternalRuleType  # noqa: E402
from gbnf.utils.errors.build_error_position import build_error_position  # noqa: E402
from gbnf.utils.errors.get_input_as_string import get_input_as_string  # noqa: E402
from gbnf.utils.errors.grammar_parse_error import GrammarParseError  # noqa: E402
from gbnf.utils.is_point_in_range import is_point_in_range  # noqa: E402


class ParseSpaceTest(unittest.TestCase):
    def test_skips_spaces_and_tabs(self) -> None:
        self.assertEqual(3, parse_space("  \tx", 0, False))

    def test_stops_at_newline_when_not_allowed(self) -> None:
        self.assertEqual(2, parse_space("  \n  x", 0, False))

    def test_consumes_newlines_when_allowed(self) -> None:
        self.assertEqual(5, parse_space("  \n  x", 0, True))

    def test_skips_comments_to_end_of_line(self) -> None:
        self.assertEqual(len("# comment"), parse_space("# comment\nx", 0, False))
        self.assertEqual(10, parse_space("# comment\nx", 0, True))

    def test_handles_end_of_input(self) -> None:
        self.assertEqual(3, parse_space("   ", 0, True))
        self.assertEqual(5, parse_space("abc", 5, True))


class ParseNameTest(unittest.TestCase):
    def test_reads_letters_and_hyphens(self) -> None:
        self.assertEqual("my-rule", parse_name("my-rule ::= x", 0))

    def test_stops_at_a_non_name_character(self) -> None:
        self.assertEqual("root", parse_name("root ::= x", 0))

    def test_raises_when_no_name_is_present(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            parse_name("::= x", 0)
        self.assertIn(PARSE_NAME_ERROR, str(ctx.exception))

    def test_raises_on_trailing_underscore_or_digit(self) -> None:
        for grammar, char in (("root_ ::= x", "_"), ("root1 ::= x", "1")):
            with self.assertRaises(GrammarParseError) as ctx:
                parse_name(grammar, 0)
            self.assertIn(GET_INVALID_CHAR_ERROR(char), str(ctx.exception))


class ParseCharTest(unittest.TestCase):
    def test_plain_character(self) -> None:
        self.assertEqual((ord("a"), 1), parse_char("abc", 0))

    def test_escapes(self) -> None:
        self.assertEqual((ord("\t"), 2), parse_char("\\t", 0))
        self.assertEqual((ord("\r"), 2), parse_char("\\r", 0))
        self.assertEqual((ord("\n"), 2), parse_char("\\n", 0))
        self.assertEqual((ord('"'), 2), parse_char('\\"', 0))
        self.assertEqual((ord("["), 2), parse_char("\\[", 0))
        self.assertEqual((ord("]"), 2), parse_char("\\]", 0))
        self.assertEqual((ord("\\"), 2), parse_char("\\\\", 0))

    def test_numeric_escapes(self) -> None:
        self.assertEqual((0x41, 4), parse_char("\\x41", 0))
        self.assertEqual((0x00E9, 6), parse_char("\\u00e9", 0))
        self.assertEqual((0x0001F600, 10), parse_char("\\U0001F600", 0))

    def test_unknown_escape_raises(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            parse_char("\\q", 0)
        self.assertIn("Unknown escape", str(ctx.exception))

    def test_end_of_input_raises(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            parse_char("abc", 5)
        self.assertIn("Unexpected end of grammar input", str(ctx.exception))


class IsWordCharTest(unittest.TestCase):
    def test_letters_only(self) -> None:
        self.assertTrue(is_word_char("a"))
        self.assertTrue(is_word_char("Z"))
        self.assertFalse(is_word_char("1"))
        self.assertFalse(is_word_char("-"))
        self.assertFalse(is_word_char(""))


class IsPointInRangeTest(unittest.TestCase):
    def test_inclusive_bounds(self) -> None:
        self.assertTrue(is_point_in_range(97, [97, 122]))
        self.assertTrue(is_point_in_range(122, [97, 122]))
        self.assertTrue(is_point_in_range(100, [97, 122]))
        self.assertFalse(is_point_in_range(96, [97, 122]))
        self.assertFalse(is_point_in_range(123, [97, 122]))


class BuildErrorPositionTest(unittest.TestCase):
    def test_empty_input(self) -> None:
        self.assertEqual(["No input provided"], build_error_position("", 0))

    def test_single_line(self) -> None:
        self.assertEqual(["abc", " ^"], build_error_position("abc", 1))

    def test_shows_up_to_three_preceding_lines(self) -> None:
        src = "one\ntwo\nthree\nfour\nfive"
        lines = build_error_position(src, len("one\ntwo\nthree\nfo"))
        self.assertEqual(3, len(lines) - 1)
        self.assertEqual("^", lines[-1].strip())

    def test_position_past_the_end_of_input(self) -> None:
        # the reference produces a trailing empty line here; the port matches it
        self.assertEqual(["ab", "", "   ^"], build_error_position("ab", 5))


class GetInputAsCodePointsTest(unittest.TestCase):
    def test_string(self) -> None:
        self.assertEqual([97, 98], get_input_as_code_points("ab"))

    def test_single_code_point(self) -> None:
        self.assertEqual([97], get_input_as_code_points(97))

    def test_list_of_code_points(self) -> None:
        self.assertEqual([97, 98], get_input_as_code_points([97, 98]))


class GetInputAsStringTest(unittest.TestCase):
    def test_round_trips_code_points(self) -> None:
        self.assertEqual("ab", get_input_as_string([97, 98]))
        self.assertEqual("a", get_input_as_string(97))
        self.assertEqual("ab", get_input_as_string("ab"))
        self.assertEqual("", get_input_as_string(""))


class SymbolIdsTest(unittest.TestCase):
    def test_stores_and_reverses(self) -> None:
        ids = SymbolIds()
        ids.set("root", 0, 0)
        ids.set("other", 1, 12)
        self.assertEqual(2, ids.size)
        self.assertEqual(0, ids.get("root"))
        self.assertEqual("other", ids.reverse_get(1))
        self.assertEqual(12, ids.get_pos("other"))
        self.assertTrue(ids.has("root"))
        self.assertFalse(ids.has("missing"))
        self.assertEqual(["root", "other"], list(ids.keys()))
        self.assertEqual([("root", 0), ("other", 1)], list(ids))

    def test_missing_lookups_raise(self) -> None:
        ids = SymbolIds()
        for call in (lambda: ids.get("x"), lambda: ids.get_pos("x"), lambda: ids.reverse_get(1)):
            with self.assertRaises(KeyError):
                call()


class GenericSetTest(unittest.TestCase):
    def test_deduplicates_by_key(self) -> None:
        class Element:  # identity-hashed, like the nodes/rules the set really holds
            def __init__(self, id: int, tag: str) -> None:
                self.id, self.tag = id, tag

        gset: GenericSet = GenericSet(lambda el: el.id)
        first = Element(1, "a")
        duplicate = Element(1, "b")
        gset.add(first)
        gset.add(duplicate)
        self.assertEqual(1, gset.size)
        self.assertIs(first, gset.get(duplicate))
        self.assertTrue(gset.has(first))
        self.assertFalse(gset.has(duplicate))

    def test_preserves_insertion_order(self) -> None:
        gset: GenericSet = GenericSet(lambda el: el)
        for value in ("c", "a", "b"):
            gset.add(value)
        self.assertEqual(["c", "a", "b"], list(gset))

    def test_delete(self) -> None:
        gset: GenericSet = GenericSet(lambda el: el)
        gset.add("a")
        gset.delete("a")
        self.assertEqual(0, gset.size)
        with self.assertRaises(ValueError):
            gset.delete("a")


class SerializedRuleKeyTest(unittest.TestCase):
    def test_distinguishes_rule_types(self) -> None:
        keys = {
            get_serialized_rule_key(RuleEnd()),
            get_serialized_rule_key(RuleChar([97])),
            get_serialized_rule_key(RuleCharExclude([97])),
            get_serialized_rule_key(RuleRef(1)),
        }
        self.assertEqual(4, len(keys))

    def test_identical_rules_share_a_key(self) -> None:
        self.assertEqual(
            get_serialized_rule_key(RuleChar([97, [98, 99]])),
            get_serialized_rule_key(RuleChar([97, [98, 99]])),
        )

    def test_unknown_rule_raises(self) -> None:
        with self.assertRaises(ValueError):
            get_serialized_rule_key(object())


class RulesBuilderTest(unittest.TestCase):
    def defs(self, grammar: str):
        builder = RulesBuilder(grammar)
        return [
            [elem.to_dict() for elem in rule] if rule is not None else None
            for rule in builder.rules
        ]

    def test_single_literal(self) -> None:
        self.assertEqual(
            [[{"type": "CHAR", "value": [97]}, {"type": "END"}]], self.defs('root ::= "a"')
        )

    def test_alternates_insert_an_alt_marker(self) -> None:
        self.assertEqual(
            [
                [
                    {"type": "CHAR", "value": [97]},
                    {"type": "ALT"},
                    {"type": "CHAR", "value": [98]},
                    {"type": "END"},
                ]
            ],
            self.defs('root ::= "a" | "b"'),
        )

    def test_ranges_use_char_rng_upper(self) -> None:
        self.assertEqual(
            [
                [
                    {"type": "CHAR", "value": [97]},
                    {"type": "CHAR_RNG_UPPER", "value": 122},
                    {"type": "END"},
                ]
            ],
            self.defs("root ::= [a-z]"),
        )

    def test_negation_uses_char_not(self) -> None:
        self.assertEqual(InternalRuleType.CHAR_NOT.value, self.defs("root ::= [^a]")[0][0]["type"])

    def test_quantifiers_generate_sub_rules(self) -> None:
        builder = RulesBuilder('root ::= "a"*')
        self.assertEqual(2, len(builder.rules))
        self.assertEqual("root_1", builder.symbol_ids.reverse_get(1))

    def test_symbol_ids_are_assigned_in_order_of_appearance(self) -> None:
        builder = RulesBuilder('root ::= a b\na ::= "1"\nb ::= "2"')
        self.assertEqual([("root", 0), ("a", 1), ("b", 2)], list(builder.symbol_ids))

    def test_undefined_reference_is_reported(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            RulesBuilder("root ::= missing")
        self.assertIn('Undefined rule identifier "missing"', str(ctx.exception))

    def test_time_limit_is_enforced(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            RulesBuilder('root ::= "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"', limit=-1)
        self.assertIn("duration of -1 exceeded", str(ctx.exception))


class BuildRuleStackTest(unittest.TestCase):
    def stack(self, grammar: str, rule_id: int = 0):
        return build_rule_stack(RulesBuilder(grammar).rules[rule_id])

    def test_single_path(self) -> None:
        stack = self.stack('root ::= "ab"')
        self.assertEqual(1, len(stack))
        self.assertEqual([RuleChar([97]), RuleChar([98]), RuleEnd()], stack[0])

    def test_alternates_split_into_paths(self) -> None:
        stack = self.stack('root ::= "a" | "b"')
        self.assertEqual([[RuleChar([97]), RuleEnd()], [RuleChar([98]), RuleEnd()]], stack)

    def test_ranges_collapse_into_a_single_rule(self) -> None:
        self.assertEqual([[RuleChar([[97, 122]]), RuleEnd()]], self.stack("root ::= [a-z]"))

    def test_char_alternates_collapse_into_a_single_rule(self) -> None:
        self.assertEqual([[RuleChar([97, 98, 99]), RuleEnd()]], self.stack("root ::= [abc]"))

    def test_negated_ranges(self) -> None:
        self.assertEqual(
            [[RuleCharExclude([[97, 122], 95]), RuleEnd()]], self.stack("root ::= [^a-z_]")
        )

    def test_references_become_rule_refs(self) -> None:
        stack = self.stack('root ::= other\nother ::= "a"')
        self.assertIsInstance(stack[0][0], RuleRef)
        self.assertEqual(1, stack[0][0].value)

    def test_every_path_terminates_with_end(self) -> None:
        for path in self.stack('root ::= "a" | "b" | "c"'):
            self.assertIsInstance(path[-1], RuleEnd)


class RuleRefTest(unittest.TestCase):
    def test_nodes_must_be_set_before_reading(self) -> None:
        with self.assertRaises(ValueError):
            RuleRef(0).nodes

    def test_nodes_are_deduplicated_and_ordered(self) -> None:
        ref = RuleRef(0)
        first, second = object(), object()
        ref.nodes = [first, second, first]
        self.assertEqual([first, second], ref.nodes)


if __name__ == "__main__":
    unittest.main()
