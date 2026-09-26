import unittest

from gbnf import GBNF, GrammarParseError

from ..helpers import load_fixture

VALID_GRAMMARS, INVALID_GRAMMARS = load_fixture("validate-grammar")


class TestValidateGrammar(unittest.TestCase):
    def test_it_parses_a_grammar(self):
        for idx, grammar in enumerate(VALID_GRAMMARS):
            with self.subTest(idx=idx, grammar=grammar):
                self.assertTrue(GBNF(grammar))

    def test_it_reports_an_error_for_an_invalid_grammar(self):
        for idx, (grammar, error_pos, error_reason) in enumerate(INVALID_GRAMMARS):
            with self.subTest(idx=idx, grammar=grammar):
                expected = GrammarParseError(grammar, error_pos, error_reason)
                with self.assertRaises(GrammarParseError) as ctx:
                    GBNF(grammar)
                self.assertEqual(str(ctx.exception), str(expected))


if __name__ == "__main__":
    unittest.main()
