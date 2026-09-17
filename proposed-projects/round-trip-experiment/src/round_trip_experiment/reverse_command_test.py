from pathlib import Path

import pytest

from round_trip_experiment.reverse_command import reverse_command

CONDITION = {
    "source_language": "typescript",
    "include_typescript_tests": True,
    "include_python_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}
PLACES = dict(
    staged_derivations_directory=Path("/cache/round-trip-experiment/derivations/20260909T001426Z_1c28aa33"),
    reverse_run_root=Path("/repo/proposed-projects/round-trip-experiment/reverse/20260909T001426Z_1c28aa33"),
    gbnf_experiment_directory=Path("/repo/packages/gbnf-experiment"),
)


@pytest.fixture
def command():
    return reverse_command(condition=CONDITION, **PLACES)


def describe_reverse_command():
    def it_invokes_run_gbnf_experiment_in_the_gbnf_experiment_package(command):
        assert command["argv"][:5] == [
            "uv", "run", "--directory", "/repo/packages/gbnf-experiment", "run-gbnf-experiment",
        ]

    def it_passes_the_reverse_condition_with_both_suites(command):
        assert command["argv"][5:] == [
            "--source-language", "typescript",
            "--include-typescript-tests",
            "--include-python-tests",
            "--effort", "high",
            "--model", "claude-opus-5",
        ]

    def it_omits_a_suite_the_condition_turns_off():
        command = reverse_command(condition={**CONDITION, "include_python_tests": False}, **PLACES)
        assert "--include-python-tests" not in command["argv"]

    def it_reads_the_reference_from_the_staged_derivations_root(command):
        assert command["env"]["GBNF_EXPERIMENT_PREPARED_DIRECTORY"] == (
            "/cache/round-trip-experiment/derivations/20260909T001426Z_1c28aa33"
        )

    def it_banks_the_run_under_the_forward_runs_own_reverse_root(command):
        assert command["env"]["GBNF_EXPERIMENT_DATA_DIRECTORY"] == (
            "/repo/proposed-projects/round-trip-experiment/reverse/20260909T001426Z_1c28aa33"
        )

    def it_sets_no_other_environment(command):
        assert set(command["env"]) == {
            "GBNF_EXPERIMENT_PREPARED_DIRECTORY",
            "GBNF_EXPERIMENT_DATA_DIRECTORY",
        }
