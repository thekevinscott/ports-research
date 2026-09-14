"""Public API tests for the Python port, including the reference README's examples."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gbnf import (  # noqa: E402
    GBNF,
    GrammarParseError,
    InputParseError,
    ParseState,
    RuleChar,
    RuleCharExclude,
    RuleEnd,
    RuleType,
    is_range,
)


def rules(state: ParseState):
    return [rule.to_dict() for rule in state]


class ReadmeExamplesTest(unittest.TestCase):
    def test_yes_no_grammar(self) -> None:
        state = GBNF('\nroot  ::= "yes" | "no"\n')
        self.assertEqual(
            [
                {"type": "char", "value": [ord("y")]},
                {"type": "char", "value": [ord("n")]},
            ],
            rules(state),
        )

    def test_state_is_immutable_across_add(self) -> None:
        state = GBNF('\nroot  ::= "I like green eggs and ham"\n')
        self.assertEqual([{"type": "char", "value": [ord("I")]}], rules(state))

        after_first = state.add("I li")
        self.assertEqual([{"type": "char", "value": [ord("k")]}], rules(after_first))
        # the original state is unchanged
        self.assertEqual([{"type": "char", "value": [ord("I")]}], rules(state))

        after_second = after_first.add("ke gree")
        self.assertEqual([{"type": "char", "value": [ord("n")]}], rules(after_second))

    def test_state_can_be_cast_to_a_list_and_indexed(self) -> None:
        state = GBNF('root ::= "ab"')
        self.assertEqual({"type": "char", "value": [ord("a")]}, list(state)[0].to_dict())

    def test_invalid_grammar_throws(self) -> None:
        with self.assertRaises(GrammarParseError):
            GBNF("root")  # a rule with no `::=`

    def test_body_less_root_is_valid_and_immediately_complete(self) -> None:
        self.assertEqual([{"type": "end"}], rules(GBNF("root ::= ")))

    def test_initial_string_is_parsed(self) -> None:
        state = GBNF('root ::= "abc"', "ab")
        self.assertEqual([{"type": "char", "value": [ord("c")]}], rules(state))


class ParseStateTest(unittest.TestCase):
    def test_is_callable_like_the_js_proxy(self) -> None:
        state = GBNF('root ::= "abc"')
        self.assertEqual(rules(state("a")), rules(state.add("a")))

    def test_size_and_len(self) -> None:
        state = GBNF('root ::= "a" | "b" | "c"')
        self.assertEqual(3, state.size)
        self.assertEqual(3, len(state))

    def test_grammar_is_exposed(self) -> None:
        grammar = 'root ::= "a"'
        self.assertEqual(grammar, GBNF(grammar).grammar)

    def test_iteration_deduplicates_identical_rules(self) -> None:
        # both alternates start with the same character
        state = GBNF('root ::= "ab" | "ac"')
        self.assertEqual([{"type": "char", "value": [ord("a")]}], rules(state))

    def test_end_rule_marks_a_valid_stopping_point(self) -> None:
        state = GBNF('root ::= "a"').add("a")
        self.assertEqual([{"type": "end"}], rules(state))
        self.assertEqual(RuleType.END, list(state)[0].type)

    def test_add_accepts_a_code_point(self) -> None:
        state = GBNF('root ::= "abc"')
        self.assertEqual(rules(state.add(ord("a"))), rules(state.add("a")))

    def test_add_accepts_a_list_of_code_points(self) -> None:
        state = GBNF('root ::= "abc"')
        self.assertEqual(rules(state.add([ord("a"), ord("b")])), rules(state.add("ab")))


class RuleTest(unittest.TestCase):
    def test_char_rule_shape(self) -> None:
        rule = list(GBNF('root ::= "a"'))[0]
        self.assertIsInstance(rule, RuleChar)
        self.assertEqual(RuleType.CHAR, rule.type)
        self.assertEqual([ord("a")], rule.value)
        # rules compare equal to their plain-object form, like the reference's objects
        self.assertEqual({"type": "char", "value": [97]}, rule)
        self.assertEqual("char", rule["type"])

    def test_excluded_char_rule_shape(self) -> None:
        rule = list(GBNF("root ::= [^a-z]"))[0]
        self.assertIsInstance(rule, RuleCharExclude)
        self.assertEqual(RuleType.CHAR_EXCLUDE, rule.type)
        self.assertEqual([[ord("a"), ord("z")]], rule.value)

    def test_end_rule_shape(self) -> None:
        rule = list(GBNF('root ::= "a"').add("a"))[0]
        self.assertIsInstance(rule, RuleEnd)
        self.assertEqual({"type": "end"}, rule.to_dict())

    def test_ranges(self) -> None:
        rule = list(GBNF("root ::= [a-z0-9]"))[0]
        self.assertEqual([[97, 122], [48, 57]], rule.value)
        self.assertTrue(all(is_range(value) for value in rule.value))

    def test_mixed_ranges_and_code_points(self) -> None:
        rule = list(GBNF("root ::= [a-z_]"))[0]
        self.assertEqual([[97, 122], 95], rule.value)
        self.assertTrue(is_range(rule.value[0]))
        self.assertFalse(is_range(rule.value[1]))

    def test_is_range_rejects_non_ranges(self) -> None:
        self.assertFalse(is_range(1))
        self.assertFalse(is_range([1]))
        self.assertFalse(is_range([1, 2, 3]))
        self.assertFalse(is_range(["a", "b"]))
        self.assertTrue(is_range([1, 2]))


class MatchingTest(unittest.TestCase):
    def test_ranges_match(self) -> None:
        for char in ("a", "m", "z"):
            self.assertEqual([{"type": "end"}], rules(GBNF("root ::= [a-z]", char)))

    def test_excluded_ranges_match_outside_the_range(self) -> None:
        self.assertEqual([{"type": "end"}], rules(GBNF("root ::= [^a-z]", "A")))
        with self.assertRaises(InputParseError):
            GBNF("root ::= [^a-z]", "a")

    def test_repetition(self) -> None:
        # after any number of "a"s the grammar may take another "a" or stop
        expected = [{"type": "char", "value": [ord("a")]}, {"type": "end"}]
        self.assertEqual(expected, rules(GBNF('root ::= "a"*', "aaaa")))
        self.assertEqual(expected, rules(GBNF('root ::= "a"*', "")))
        with self.assertRaises(InputParseError):
            GBNF('root ::= "a"+', "b")

    def test_recursion(self) -> None:
        grammar = 'root ::= "(" root ")" | "x"'
        self.assertEqual([{"type": "end"}], rules(GBNF(grammar, "((x))")))
        # an unbalanced prefix is still a valid partial parse, so it must not raise
        self.assertEqual([{"type": "char", "value": [ord(")")]}], rules(GBNF(grammar, "((x)")))
        with self.assertRaises(InputParseError):
            GBNF(grammar, "(y")

    def test_rule_references(self) -> None:
        grammar = 'root ::= greeting " " name\ngreeting ::= "hi" | "hello"\nname ::= [a-z]+'
        # "h" may continue into either "hi" or "hello"
        self.assertEqual(
            [{"type": "char", "value": [ord("i")]}, {"type": "char", "value": [ord("e")]}],
            rules(GBNF(grammar, "h")),
        )
        state = GBNF(grammar, "hello bob")
        self.assertIn({"type": "end"}, rules(state))

    def test_comments_and_whitespace_are_ignored(self) -> None:
        state = GBNF('# a comment\nroot ::= "a" # another\n')
        self.assertEqual([{"type": "char", "value": [ord("a")]}], rules(state))


class GrammarErrorTest(unittest.TestCase):
    def test_empty_grammar(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("")
        self.assertIn("No rules were found", str(ctx.exception))
        self.assertIn("No input provided", str(ctx.exception))

    def test_undefined_rule_reference(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("root ::= foo")
        self.assertIn('Undefined rule identifier "foo"', str(ctx.exception))

    def test_missing_assignment(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('root "a"')
        self.assertIn("Expecting ::=", str(ctx.exception))

    def test_invalid_name_character(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('root_ ::= "a"')
        self.assertIn('Invalid character "_"', str(ctx.exception))

    def test_unclosed_group(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('root ::= ("a"')
        self.assertIn("Expecting ')'", str(ctx.exception))

    def test_quantifier_without_preceding_item(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("root ::= *")
        self.assertIn("Expecting preceding item to */+/?", str(ctx.exception))

    def test_unknown_escape(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('root ::= "\\q"')
        self.assertIn("Unknown escape", str(ctx.exception))

    def test_error_carries_grammar_position_and_reason(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("root ::= foo")
        self.assertEqual("root ::= foo", ctx.exception.grammar)
        self.assertEqual('Undefined rule identifier "foo"', ctx.exception.reason)
        self.assertIsInstance(ctx.exception.pos, int)


class InputErrorTest(unittest.TestCase):
    def test_rejects_input_that_does_not_match(self) -> None:
        with self.assertRaises(InputParseError) as ctx:
            GBNF('root ::= "abc"', "axc")
        self.assertEqual("Failed to parse input string:\n\naxc\n ^", str(ctx.exception))

    def test_rejects_input_past_the_end(self) -> None:
        with self.assertRaises(InputParseError):
            GBNF('root ::= "a"', "aa")

    def test_error_points_at_the_position_across_adds(self) -> None:
        state = GBNF('root ::= "abc"').add("ab")
        with self.assertRaises(InputParseError) as ctx:
            state.add("X")
        self.assertEqual("abX", ctx.exception.src)
        self.assertEqual(
            "Failed to parse input string:\n\nX\n^", ctx.exception.error_for_most_recent_input
        )


if __name__ == "__main__":
    unittest.main()
