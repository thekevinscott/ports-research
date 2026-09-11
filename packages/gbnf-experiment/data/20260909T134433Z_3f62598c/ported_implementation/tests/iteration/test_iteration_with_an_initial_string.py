import unittest

from gbnf import GBNF

from ..helpers import load_fixture, to_rules

(CASES,) = load_fixture("iteration-with-an-initial-string")


class TestIterationWithAnInitialString(unittest.TestCase):
    def test_it_returns_parse_state_for_a_grammar_and_initial_string(self):
        for idx, (grammar, input_, expected) in enumerate(CASES):
            with self.subTest(idx=idx, grammar=grammar, input=input_):
                state = GBNF(grammar)
                state = state.add(input_)
                self.assertEqual(list(state), to_rules(expected))


if __name__ == "__main__":
    unittest.main()
