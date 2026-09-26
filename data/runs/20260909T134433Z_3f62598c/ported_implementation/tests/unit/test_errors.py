"""Ported from the reference implementation's unit tests for the error helpers."""

import unittest

from gbnf import GrammarParseError, InputParseError
from gbnf.grammar_graph.get_input_as_code_points import get_input_as_code_points
from gbnf.utils.errors.build_error_position import build_error_position
from gbnf.utils.errors.get_input_as_string import get_input_as_string
from gbnf.utils.errors.grammar_parse_error import GRAMMAR_PARSER_ERROR_HEADER_MESSAGE
from gbnf.utils.errors.input_parse_error import INPUT_PARSER_ERROR_HEADER_MESSAGE

POSITION_CASES = [
    ("root ::= \"foo\"", 1, ["root ::= \"foo\"", " ^"]),
    ("root ::= \"foo\"", 5, ["root ::= \"foo\"", "     ^"]),
    # multi line grammars with pos on first line
    ("aa\\nbb", 1, ["aa", " ^"]),
    # multi line grammars with pos on second line, first character
    ("aa\\nbb", 2, ["aa\\nbb", "^"]),
    # multi line grammars with pos on second line, second character
    ("aa\\nbb", 2 + 1, ["aa\\nbb", " ^"]),
    # multi line grammars beyond error with pos on second line
    ("aa\\nbb\\ncc", 2 + 1, ["aa\\nbb", " ^"]),
    # multi line grammars beyond error with pos on third line, first char
    ("aa\\nbb\\ncc", 2 + 2 + 0, ["aa\\nbb\\ncc", "^"]),
    # multi line grammars beyond error with pos on third line, second char
    ("aa\\nbb\\ncc", 2 + 2 + 1, ["aa\\nbb\\ncc", " ^"]),
    # multi line grammars beyond error with pos on fourth line, first char
    ("aa\\nbb\\ncc\\ndd", 2 + 2 + 2 + 0, ["bb\\ncc\\ndd", "^"]),
    # multi line grammars beyond error with pos on fifth line, second char
    ("aa\\nbb\\ncc\\ndd\\nee", 2 + 2 + 2 + 2 + 1, ["cc\\ndd\\nee", " ^"]),
]


class TestBuildErrorPosition(unittest.TestCase):
    def test_it_correctly_shows_position(self):
        for grammar, pos, (grammar_out, pos_out) in POSITION_CASES:
            with self.subTest(grammar=grammar, pos=pos):
                result = build_error_position("\n".join(grammar.split("\\n")), pos)
                self.assertEqual(result, [*grammar_out.split("\\n"), pos_out])

    def test_it_renders_a_message_for_empty_input(self):
        self.assertEqual(build_error_position("", 0), ["No input provided"])


class TestGetInputAsString(unittest.TestCase):
    def test_it_correctly_converts_input_to_string(self):
        cases = [
            ("hello", "hello"),
            ([104, 101, 108, 108, 111], "hello"),
            (104, "h"),
            (0x1F600, "😀"),
            ([0x1F600, 0x1F601], "😀😁"),
        ]
        for input_, expected in cases:
            with self.subTest(input=input_):
                self.assertEqual(get_input_as_string(input_), expected)


class TestGetInputAsCodePoints(unittest.TestCase):
    def test_it_returns_code_points_for_string(self):
        self.assertEqual(get_input_as_code_points("abc"), [97, 98, 99])

    def test_it_returns_code_points_for_number(self):
        self.assertEqual(get_input_as_code_points(99), [99])

    def test_it_returns_code_points_for_list_of_numbers(self):
        self.assertEqual(get_input_as_code_points([99, 100, 101]), [99, 100, 101])


class TestGrammarParseError(unittest.TestCase):
    def test_it_renders_a_message(self):
        grammar = "aa\\nbb\\ncc\\ndd\\nee"
        pos = 5
        reason = "reason"
        err = GrammarParseError("\n".join(grammar.split("\\n")), pos, reason)
        self.assertEqual(
            str(err),
            "\n".join(
                [
                    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE(reason),
                    "",
                    "aa",
                    "bb",
                    "cc",
                    " ^",
                ]
            ),
        )


class TestInputParseError(unittest.TestCase):
    def test_it_renders_a_message(self):
        input_ = "some input"
        err = InputParseError(input_, 1)
        self.assertEqual(
            str(err),
            "\n".join([INPUT_PARSER_ERROR_HEADER_MESSAGE, "", input_, " ^"]),
        )

    def test_it_renders_a_message_for_code_point(self):
        err = InputParseError("a", 0)
        self.assertEqual(
            str(err), "\n".join([INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "a", "^"])
        )

    def test_it_renders_a_message_for_code_points(self):
        err = InputParseError("abcd", 2)
        self.assertEqual(
            str(err),
            "\n".join([INPUT_PARSER_ERROR_HEADER_MESSAGE, "", "abcd", "  ^"]),
        )


if __name__ == "__main__":
    unittest.main()
