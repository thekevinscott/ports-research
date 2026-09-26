import pytest
from gbnf import GBNF


def describe_grammars():
    def _load_cases():
        import json
        from pathlib import Path

        grammars_dir = Path(__file__).parent / "grammars"
        cases = []
        for grammar_path in sorted(grammars_dir.glob("*.gbnf")):
            json_path = grammar_path.with_suffix(".json")
            grammar = grammar_path.read_text()
            for test_case in json.loads(json_path.read_text()):
                cases.append((grammar_path.stem, test_case, grammar))
        if not cases:
            raise Exception("No grammar test cases found")
        return cases

    @pytest.mark.parametrize(("key", "test_case", "grammar"), _load_cases())
    def test_it_parses_a_known_valid_grammar(key, test_case, grammar):
        state = GBNF(grammar)
        for char in test_case:
            state = state.add(char)
