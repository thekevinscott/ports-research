import unittest

from gbnf import GBNF

from ..helpers import load_fixture, to_rules

(CASES,) = load_fixture("iteration")


class TestIteration(unittest.TestCase):
    def test_it_returns_parse_state_for_a_grammar(self):
        for idx, (grammar, expected) in enumerate(CASES):
            with self.subTest(idx=idx, grammar=grammar):
                state = GBNF(grammar)
                self.assertEqual(list(state), to_rules(expected))


if __name__ == "__main__":
    unittest.main()
