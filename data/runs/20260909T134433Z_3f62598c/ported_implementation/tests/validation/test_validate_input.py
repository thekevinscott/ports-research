import unittest

from gbnf import GBNF, InputParseError

from ..helpers import load_fixture

VALID_INPUTS, INVALID_INPUTS = load_fixture("validate-input")


class TestValidateInput(unittest.TestCase):
    def test_it_parses_a_grammar_and_input(self):
        for idx, (grammar, input_) in enumerate(VALID_INPUTS):
            with self.subTest(idx=idx, grammar=grammar, input=input_):
                self.assertTrue(GBNF(grammar, input_))

    def test_it_reports_an_error_for_an_invalid_input(self):
        for idx, (grammar, input_, error_pos) in enumerate(INVALID_INPUTS):
            with self.subTest(idx=idx, grammar=grammar, input=input_):
                expected = InputParseError(input_, error_pos, "")
                with self.assertRaises(InputParseError) as ctx:
                    graph = GBNF(grammar)
                    graph.add(input_)
                self.assertEqual(str(ctx.exception), str(expected))


if __name__ == "__main__":
    unittest.main()
