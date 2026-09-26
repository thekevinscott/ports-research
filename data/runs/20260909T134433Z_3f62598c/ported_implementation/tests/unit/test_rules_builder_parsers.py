"""Ported from the reference implementation's unit tests for the small parsers."""

import unittest

from gbnf import GrammarParseError
from gbnf.rules_builder.is_word_char import is_word_char
from gbnf.rules_builder.parse_char import parse_char
from gbnf.rules_builder.parse_name import (
    GET_INVALID_CHAR_ERROR,
    PARSE_NAME_ERROR,
    parse_name,
)
from gbnf.rules_builder.parse_space import parse_space

PREFIX = 'root ::= "'


class TestParseChar(unittest.TestCase):
    def test_it_parses_plain_chars(self):
        for char in ["a", "9"]:
            with self.subTest(char=char):
                grammar = f'root ::= "{char}" "foo"'
                self.assertEqual(parse_char(grammar, len(PREFIX)), (ord(char), 1))

    def test_it_parses_escaped_chars(self):
        cases = [
            ("escaped 8-bit unicode char", "\\x2A", ord("\x2a"), 4),
            ("escaped 16-bit unicode char", "\\u006F", ord("o"), 6),
            ("escaped 32-bit unicode char", "\\U0001F4A9", 128169, 10),
            ("escaped tab char", "\\t", ord("\t"), 2),
            ("escaped new line char", "\\n", ord("\n"), 2),
            ("escaped \r char", "\\r", ord("\r"), 2),
            ("escaped quote char", '\\"', ord('"'), 2),
            ("escaped [ char", "\\[", ord("["), 2),
            ("escaped ] char", "\\]", ord("]"), 2),
            ("escaped \\ char", "\\\\", ord("\\"), 2),
        ]
        for key, escaped_char, code_point, inc_pos in cases:
            with self.subTest(key=key, escaped_char=escaped_char):
                grammar = f'root ::= "{escaped_char}" "foo"'
                self.assertEqual(
                    parse_char(grammar, len(PREFIX)), (code_point, inc_pos)
                )

    def test_it_throws_on_invalid_input(self):
        with self.assertRaises(GrammarParseError):
            parse_char("", 0)
        with self.assertRaises(GrammarParseError):
            parse_char("a", 1)


class TestParseName(unittest.TestCase):
    def test_valid_names(self):
        for src in [
            "v",
            "valid",
            "valid-name",
            "valid-name-foo",
            "validName",
            "validName-foo",
        ]:
            with self.subTest(src=src):
                self.assertEqual(parse_name(src, 0), src)

    def test_valid_names_at_a_non_zero_position(self):
        cases = [
            ("123valid", 3, "valid"),
            ("123valid-name", 3, "valid-name"),
            ("123valid _Name", 3, "valid"),
            ("123valid\\n_Name", 3, "valid"),
            ("123valid\\t_Name", 3, "valid"),
            ("123valid\\r_Name", 3, "valid"),
        ]
        for src, position, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(
                    parse_name("\n".join(src.split("\\n")), position), expected
                )

    def test_invalid_names(self):
        cases = [
            ("123", GrammarParseError("123", 0, PARSE_NAME_ERROR)),
            (
                "valid_name",
                GrammarParseError("valid_name", 5, GET_INVALID_CHAR_ERROR("_")),
            ),
            (
                "valid123",
                GrammarParseError("valid123", 5, GET_INVALID_CHAR_ERROR("1")),
            ),
        ]
        for src, error in cases:
            with self.subTest(src=src):
                with self.assertRaises(GrammarParseError) as ctx:
                    parse_name(src, 0)
                self.assertEqual(str(ctx.exception), str(error))


class TestParseSpace(unittest.TestCase):
    def test_parse_space(self):
        cases = [
            ("abcdefghijk", True, "abcdefghijk"),
            ("   \t   abcdefghijk", True, "abcdefghijk"),
            ("\n\n\r\n\r\nabcdefghijk", True, "abcdefghijk"),
            ("\n\n\r\n\r\nabcdefghijk", False, "\n\n\r\n\r\nabcdefghijk"),
            ("  # This is a comment\n\t   abcdefghijk", True, "abcdefghijk"),
            (
                "\n\n # This is a comment\n\r\n\r\nabcdefghijk",
                True,
                "abcdefghijk",
            ),
            (
                "\n\n # This is a comment\n\r\n\r\nabcdefghijk",
                False,
                "\n\n # This is a comment\n\r\n\r\nabcdefghijk",
            ),
            ("  \t# Comment\n# Another comment\n\n", True, ""),
            ("", True, ""),
        ]
        for input_, newline_ok, expected in cases:
            with self.subTest(input=input_, newline_ok=newline_ok):
                pos = parse_space(input_, 0, newline_ok)
                self.assertEqual(input_[pos:], expected)


class TestIsWordChar(unittest.TestCase):
    def test_letters(self):
        for char in ["a", "z", "A", "Z"]:
            self.assertTrue(is_word_char(char))

    def test_non_letters(self):
        for char in ["0", "9", "-", "@", "_", "?", " "]:
            self.assertFalse(is_word_char(char))


if __name__ == "__main__":
    unittest.main()
