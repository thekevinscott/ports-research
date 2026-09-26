import json

import pytest

from exercise_api.ladder_cases import ladder_cases

ARITHMETIC = "root ::= num\nnum ::= [0-9]+\n"
JSON_GRAMMAR = "root ::= object\nobject ::= \"{\" \"}\"\n"
RUNGS = [
    "1-literal",
    "2-alternation",
    *["3-repetition"] * 5,
    "4-character-classes",
    *["5-rule-references"] * 3,
    "6-arithmetic",
    *["7-json"] * 4,
    *["8-json-depth"] * 6,
]


@pytest.fixture
def grammars_dir(tmp_path):
    (tmp_path / "arithmetic.gbnf").write_text(ARITHMETIC)
    (tmp_path / "arithmetic.json").write_text(json.dumps(["1", "22", "333"]))
    (tmp_path / "json.gbnf").write_text(JSON_GRAMMAR)
    return tmp_path


def describe_ladder_cases():
    def it_emits_the_rungs_in_order(grammars_dir):
        assert [case["rung"] for case in ladder_cases(grammars_dir)] == RUNGS

    def it_gives_every_case_a_grammar_an_input_and_a_rung(grammars_dir):
        keys = {"grammar", "input", "rung", "repeat", "warmup"}
        assert all(set(case) == keys for case in ladder_cases(grammars_dir))

    def it_is_deterministic(grammars_dir):
        assert ladder_cases(grammars_dir) == ladder_cases(grammars_dir)

    def it_scales_the_repetition_rung_by_input_length(grammars_dir):
        lengths = [len(c["input"]) for c in ladder_cases(grammars_dir) if c["rung"] == "3-repetition"]
        assert lengths == [16, 64, 256, 16384, 65536]

    def it_builds_chains_of_rules_without_digits_in_the_names(grammars_dir):
        cases = [c for c in ladder_cases(grammars_dir) if c["rung"] == "5-rule-references"]
        assert [len(c["grammar"].splitlines()) for c in cases] == [33, 129, 513]
        assert not any(character.isdigit() for c in cases for character in c["grammar"])
        assert cases[0]["input"] == "x" * 31 + "leaf"
        assert cases[-1]["input"] == "x" * 511 + "leaf"

    def it_takes_the_longest_arithmetic_input_from_the_fixtures(grammars_dir):
        [case] = [c for c in ladder_cases(grammars_dir) if c["rung"] == "6-arithmetic"]
        assert case["grammar"] == ARITHMETIC
        assert case["input"] == "333"

    def it_sizes_the_flat_json_objects_exactly(grammars_dir):
        cases = [c for c in ladder_cases(grammars_dir) if c["rung"] == "7-json"]
        assert [len(c["input"]) for c in cases] == [1024, 4096, 16384, 65536]
        assert all(c["grammar"] == JSON_GRAMMAR for c in cases)

    def it_nests_the_depth_rung_inside_one_object_key(grammars_dir):
        cases = [c for c in ladder_cases(grammars_dir) if c["rung"] == "8-json-depth"]
        assert [c["input"].count("[") for c in cases] == [8, 32, 128, 512, 2048, 8192]
        assert cases[0]["input"] == '{"a":' + "[" * 8 + "]" * 8 + "}"

    def it_rejects_a_directory_without_the_fixture_grammars(tmp_path):
        with pytest.raises(FileNotFoundError):
            ladder_cases(tmp_path)

    def it_gives_the_slowest_cases_a_smaller_repeat_budget_than_the_rest(grammars_dir):
        budgets = {
            (c["rung"], len(c["input"])): (c["warmup"], c["repeat"]) for c in ladder_cases(grammars_dir)
        }
        assert budgets[("1-literal", 1)] == (3, 100)
        assert budgets[("3-repetition", 65536)] == (1, 5)
        assert budgets[("8-json-depth", 16390)] == (0, 1)
