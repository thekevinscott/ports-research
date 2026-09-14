import unittest

from gbnf import GBNF

from ..helpers import load_fixture

(CASES,) = load_fixture("grammars")


def unescape(value: str) -> str:
    return value.replace("\\n", "\n").replace("\\t", "\t")


class TestGrammars(unittest.TestCase):
    def test_it_parses_a_known_valid_grammar(self):
        for idx, (name, raw_test_case, grammar) in enumerate(CASES):
            with self.subTest(idx=idx, name=name, test_case=raw_test_case):
                test_case = unescape(raw_test_case)

                state = GBNF(unescape(grammar))

                for char in test_case:
                    state = state.add(char)


if __name__ == "__main__":
    unittest.main()
