"""Behavioural tests for the public API of the port."""

from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from ported_implementation import (  # noqa: E402
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


class ReadmeTest(unittest.TestCase):
    """The examples from the reference README."""

    def test_yes_or_no(self) -> None:
        state = GBNF('\nroot  ::= "yes" | "no"\n')
        self.assertEqual(
            list(state),
            [RuleChar(value=[ord("y")]), RuleChar(value=[ord("n")])],
        )

    def test_state_is_immutable(self) -> None:
        state = GBNF('\nroot  ::= "I like green eggs and ham"\n')
        self.assertEqual(list(state), [RuleChar(value=[ord("I")])])

        after_first = state.add("I li")
        self.assertEqual(list(after_first), [RuleChar(value=[ord("k")])])

        after_second = after_first.add("ke gree")
        self.assertEqual(list(after_second), [RuleChar(value=[ord("n")])])

        # The earlier states are unchanged.
        self.assertEqual(list(state), [RuleChar(value=[ord("I")])])
        self.assertEqual(list(after_first), [RuleChar(value=[ord("k")])])

    def test_invalid_grammar_raises(self) -> None:
        with self.assertRaises(GrammarParseError):
            GBNF("root")


class ParseStateApiTest(unittest.TestCase):
    def test_rules_iterator(self) -> None:
        state = GBNF('root ::= "a" | "b"')
        self.assertEqual(list(state.rules()), list(state))

    def test_can_be_spread_and_indexed(self) -> None:
        rules = [*GBNF('root ::= "ab" | "cd"')]
        self.assertEqual(rules[0], RuleChar(value=[ord("a")]))
        self.assertEqual(rules[1], RuleChar(value=[ord("c")]))

    def test_size(self) -> None:
        self.assertEqual(GBNF('root ::= "a" | "b" | "c"').size, 3)
        self.assertEqual(len(GBNF('root ::= "a" | "b" | "c"')), 3)

    def test_grammar_is_exposed(self) -> None:
        grammar = 'root ::= "a"'
        self.assertEqual(GBNF(grammar).grammar, grammar)

    def test_add_returns_a_new_state(self) -> None:
        state = GBNF('root ::= "ab"')
        added = state.add("a")
        self.assertIsInstance(added, ParseState)
        self.assertIsNot(added, state)

    def test_state_is_callable(self) -> None:
        state = GBNF('root ::= "ab"')
        self.assertEqual(list(state("a")), list(state.add("a")))

    def test_initial_input(self) -> None:
        self.assertEqual(list(GBNF('root ::= "abc"', "ab")), [RuleChar(value=[ord("c")])])

    def test_initial_input_as_code_points(self) -> None:
        self.assertEqual(list(GBNF('root ::= "abc"', [97, 98])), [RuleChar(value=[ord("c")])])

    def test_initial_input_as_single_code_point(self) -> None:
        self.assertEqual(list(GBNF('root ::= "abc"', 97)), [RuleChar(value=[ord("b")])])

    def test_end_rule_at_end_of_input(self) -> None:
        self.assertEqual(list(GBNF('root ::= "a"', "a")), [RuleEnd()])

    def test_duplicate_rules_are_yielded_once(self) -> None:
        self.assertEqual(list(GBNF('root ::= "a" | "a"')), [RuleChar(value=[ord("a")])])


class RuleTest(unittest.TestCase):
    def test_rule_types(self) -> None:
        self.assertEqual(RuleType.CHAR, "char")
        self.assertEqual(RuleType.CHAR_EXCLUDE, "char_exclude")
        self.assertEqual(RuleType.END, "end")

    def test_char_rule(self) -> None:
        (rule,) = GBNF("root ::= [a-z]")
        self.assertEqual(rule.type, RuleType.CHAR)
        self.assertEqual(rule.value, [[ord("a"), ord("z")]])
        self.assertTrue(is_range(rule.value[0]))

    def test_excluded_char_rule(self) -> None:
        (rule,) = GBNF("root ::= [^a-z]")
        self.assertEqual(rule.type, RuleType.CHAR_EXCLUDE)
        self.assertEqual(rule, RuleCharExclude(value=[[ord("a"), ord("z")]]))

    def test_mixed_ranges_and_code_points(self) -> None:
        (rule,) = GBNF("root ::= [a-z0_]")
        self.assertEqual(rule.value, [[ord("a"), ord("z")], ord("0"), ord("_")])

    def test_rules_are_readable_as_mappings(self) -> None:
        (rule,) = GBNF('root ::= "a"')
        self.assertEqual(rule["type"], RuleType.CHAR)
        self.assertEqual(rule["value"], [ord("a")])
        self.assertEqual(dict(rule), {"type": RuleType.CHAR, "value": [ord("a")]})
        self.assertEqual(rule, {"type": RuleType.CHAR, "value": [ord("a")]})

    def test_is_range(self) -> None:
        self.assertTrue(is_range([1, 2]))
        self.assertFalse(is_range([1]))
        self.assertFalse(is_range([1, 2, 3]))
        self.assertFalse(is_range(1))
        self.assertFalse(is_range("ab"))


class GrammarErrorTest(unittest.TestCase):
    def test_no_rules(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("")
        self.assertIn("No rules were found", str(ctx.exception))
        self.assertEqual(ctx.exception.reason, "No rules were found")
        self.assertEqual(ctx.exception.pos, 0)

    def test_missing_root_symbol(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('foo ::= "a"')
        self.assertIn("Grammar does not contain a root symbol", str(ctx.exception))
        self.assertIn('["foo"]', str(ctx.exception))

    def test_undefined_rule(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF("root ::= missing")
        self.assertIn('Undefined rule identifier "missing"', str(ctx.exception))

    def test_error_points_at_the_offending_line(self) -> None:
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF('root ::= "a" %')
        self.assertEqual(
            str(ctx.exception),
            "\n".join(
                [
                    "Failed to parse grammar: Expecting newline or end at 13",
                    "",
                    'root ::= "a" %',
                    "             ^",
                ]
            ),
        )

    def test_grammar_is_attached_to_the_error(self) -> None:
        grammar = "root ::= *"
        with self.assertRaises(GrammarParseError) as ctx:
            GBNF(grammar)
        self.assertEqual(ctx.exception.grammar, grammar)
        self.assertEqual(ctx.exception.pos, 9)

    def test_infinitely_recursive_grammar(self) -> None:
        # The reference exhausts the Javascript call stack on these.
        with self.assertRaises(RecursionError):
            GBNF("root ::= root")
        with self.assertRaises(RecursionError):
            GBNF('root ::= a*\na ::= "b"?\n', "b")


class InputErrorTest(unittest.TestCase):
    def test_invalid_first_character(self) -> None:
        with self.assertRaises(InputParseError) as ctx:
            GBNF('root ::= "abc"', "x")
        self.assertEqual(
            str(ctx.exception),
            "\n".join(["Failed to parse input string:", "", "x", "^"]),
        )

    def test_error_includes_previous_input(self) -> None:
        state = GBNF('root ::= "abc"', "ab")
        with self.assertRaises(InputParseError) as ctx:
            state.add("z")
        self.assertEqual(ctx.exception.src, "abz")
        self.assertEqual(
            str(ctx.exception),
            "\n".join(["Failed to parse input string:", "", "abz", "  ^"]),
        )
        self.assertEqual(
            ctx.exception.error_for_most_recent_input,
            "\n".join(["Failed to parse input string:", "", "z", "^"]),
        )

    def test_input_past_the_end_of_the_grammar(self) -> None:
        with self.assertRaises(InputParseError):
            GBNF('root ::= "ab"', "abc")


class GrammarFeatureTest(unittest.TestCase):
    def test_repetition(self) -> None:
        state = GBNF('root ::= "a"+', "aaa")
        self.assertEqual(list(state), [RuleChar(value=[ord("a")]), RuleEnd()])

    def test_optional(self) -> None:
        state = GBNF('root ::= "a"? "b"')
        self.assertEqual(list(state), [RuleChar(value=[ord("a")]), RuleChar(value=[ord("b")])])

    def test_group_alternates(self) -> None:
        state = GBNF('root ::= ("a" | "b") "c"', "b")
        self.assertEqual(list(state), [RuleChar(value=[ord("c")])])

    def test_rule_references(self) -> None:
        state = GBNF('root ::= greeting "!"\ngreeting ::= "hi"', "hi")
        self.assertEqual(list(state), [RuleChar(value=[ord("!")])])

    def test_comments_are_ignored(self) -> None:
        state = GBNF('# a comment\nroot ::= "a" # another\n')
        self.assertEqual(list(state), [RuleChar(value=[ord("a")])])

    def test_escapes(self) -> None:
        self.assertEqual(list(GBNF('root ::= "\\n"')), [RuleChar(value=[ord("\n")])])
        self.assertEqual(list(GBNF('root ::= "\\t"')), [RuleChar(value=[ord("\t")])])
        self.assertEqual(list(GBNF('root ::= "\\x41"')), [RuleChar(value=[ord("A")])])
        self.assertEqual(list(GBNF('root ::= "\\u00e9"')), [RuleChar(value=[ord("é")])])

    def test_non_bmp_code_points(self) -> None:
        # Python strings are sequences of code points, so astral characters are a
        # single rule here (the reference splits them into UTF-16 surrogate halves).
        state = GBNF('root ::= "\\U0001F600"')
        self.assertEqual(list(state), [RuleChar(value=[0x1F600])])
        self.assertEqual(list(state.add("😀")), [RuleEnd()])

    def test_json_grammar(self) -> None:
        grammar = """
root   ::= object
object ::= "{" ws ( string ":" ws value ("," ws string ":" ws value)* )? "}" ws
value  ::= object | string | "true" | "false" | "null"
string ::= "\\"" [a-z]* "\\"" ws
ws     ::= [ \\t\\n]*
"""
        state = GBNF(grammar, '{"a": {"b": true}}')
        self.assertIn(RuleEnd(), list(state))


if __name__ == "__main__":
    unittest.main()
