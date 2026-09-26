import unittest

from gbnf import GBNF, InputParseError

from ..helpers import load_fixture, to_rules

THROWING_CASES, PARSING_CASES, ERROR_CASES = load_fixture(
    "iteration-with-additional-strings"
)


class TestIterationWithAdditionalStrings(unittest.TestCase):
    def test_it_throws_for_invalid_additional_input(self):
        for idx, (grammar, starting, additional) in enumerate(THROWING_CASES):
            with self.subTest(
                idx=idx, grammar=grammar, starting=starting, additional=additional
            ):
                graph = GBNF(grammar, starting)
                with self.assertRaises(Exception):
                    graph.add(additional)

    def test_it_parses_a_grammar_with_starting_and_additional_input(self):
        for idx, (grammar, starting, additional, expected) in enumerate(PARSING_CASES):
            with self.subTest(
                idx=idx, grammar=grammar, starting=starting, additional=additional
            ):
                state = GBNF(grammar, starting)
                state = state.add(additional)
                self.assertEqual(list(state), to_rules(expected))

    def test_it_throws_a_particular_error(self):
        for error_for_most_recent_input in ERROR_CASES:
            with self.subTest(
                error_for_most_recent_input=error_for_most_recent_input
            ):
                grammar = 'root ::= "bar"'
                state = GBNF(grammar)
                state = state.add("b")
                state = state.add("a")
                try:
                    state.add("z")
                    self.fail("Expected an error to be thrown")
                except InputParseError as err:
                    expected_err = InputParseError("z", 0, "ba")
                    if error_for_most_recent_input:
                        self.assertEqual(
                            err.error_for_most_recent_input,
                            expected_err.error_for_most_recent_input,
                        )
                    else:
                        self.assertEqual(str(err), str(expected_err))


if __name__ == "__main__":
    unittest.main()
