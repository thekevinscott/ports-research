import pytest

from round_trip_experiment.reverse_condition import reverse_condition

FORWARD = {
    "name": "source-python_typescript-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_typescript_tests": True,
    "include_python_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}
CELLS = [
    {"include_typescript_tests": typescript, "include_python_tests": python}
    for typescript in (True, False)
    for python in (True, False)
]


def describe_reverse_condition():
    def it_reads_a_python_source_runs_port_back_from_typescript():
        assert reverse_condition(FORWARD)["source_language"] == "typescript"

    def it_reads_a_typescript_source_runs_port_back_from_python():
        forward = {**FORWARD, "source_language": "typescript"}
        assert reverse_condition(forward)["source_language"] == "python"

    def it_rejects_an_unknown_source_language():
        with pytest.raises(KeyError):
            reverse_condition({**FORWARD, "source_language": "rust"})

    def it_includes_both_suites_whatever_the_forward_cell_included():
        for cell in CELLS:
            condition = reverse_condition({**FORWARD, **cell})
            assert (condition["include_typescript_tests"], condition["include_python_tests"]) == (True, True)

    def it_carries_effort_and_model_unchanged():
        condition = reverse_condition(FORWARD)
        assert (condition["effort"], condition["model"]) == ("high", "claude-opus-5")

    def it_carries_only_the_keys_run_gbnf_experiment_takes():
        assert set(reverse_condition(FORWARD)) == {
            "source_language",
            "include_typescript_tests",
            "include_python_tests",
            "effort",
            "model",
        }
