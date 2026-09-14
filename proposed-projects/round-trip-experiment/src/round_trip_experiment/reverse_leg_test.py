from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.reverse_leg import reverse_leg

FORWARD_CONDITION = {
    "name": "source-python_python-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}
ESTIMATE = {"total_tokens": 4697263, "api_calls": 63, "duration_ms": 456517}
COMMAND = {"argv": ["uv", "run", "run-gbnf-experiment"], "env": {"GBNF_EXPERIMENT_DATA_DIRECTORY": "/reverse"}}
RUN = Path("/data/20260909T001426Z_1c28aa33")
STAGED = Path("/cache/staging/20260909T001426Z_1c28aa33/390bf534c55d496b")
PLACES = dict(
    derivation_cache_key="390bf534c55d496b",
    derivations_directory=Path("/cache/gbnf-experiment/derivations"),
    gbnf_experiment_directory=Path("/repo/packages/gbnf-experiment"),
    staging_directory=Path("/cache/staging"),
    reverse_directory=Path("/repo/proposed-projects/round-trip-experiment/reverse"),
)
REVERSE_CONDITION = {
    "source_language": "typescript",
    "include_typescript_tests": True,
    "include_python_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def load_run():
    with patch("round_trip_experiment.reverse_leg.load_run", autospec=True) as m:
        m.return_value = {"run_id": RUN.name, "condition": FORWARD_CONDITION, "estimate": ESTIMATE}
        yield m


@pytest.fixture
def stage_port():
    with patch("round_trip_experiment.reverse_leg.stage_port", autospec=True) as m:
        m.return_value = STAGED
        yield m


@pytest.fixture
def check_staged_derivation():
    with patch("round_trip_experiment.reverse_leg.check_staged_derivation", autospec=True) as m:
        yield m


@pytest.fixture
def reverse_command():
    with patch("round_trip_experiment.reverse_leg.reverse_command", autospec=True) as m:
        m.return_value = COMMAND
        yield m


@pytest.fixture
def collaborators(load_run, stage_port, check_staged_derivation, reverse_command):
    return dict(
        load_run=load_run,
        stage_port=stage_port,
        check_staged_derivation=check_staged_derivation,
        reverse_command=reverse_command,
    )


@pytest.fixture
def report(collaborators):
    return reverse_leg(RUN, **PLACES)


def describe_reverse_leg():
    def it_stages_the_port_as_the_reverse_source_languages_derived_source(report, collaborators):
        assert collaborators["stage_port"].call_args.args == (RUN,)
        assert collaborators["stage_port"].call_args.kwargs == {
            "source_language": "typescript",
            "derivation_cache_key": "390bf534c55d496b",
            "derivations_directory": PLACES["derivations_directory"],
            "staging_directory": PLACES["staging_directory"],
        }

    def it_checks_the_staged_derivation_against_the_reverse_condition(report, collaborators):
        collaborators["check_staged_derivation"].assert_called_once_with(STAGED, condition=REVERSE_CONDITION)

    def it_builds_no_command_when_the_stage_is_incomplete(collaborators):
        collaborators["check_staged_derivation"].side_effect = ValueError("staged derivation is incomplete")
        with pytest.raises(ValueError):
            reverse_leg(RUN, **PLACES)
        collaborators["reverse_command"].assert_not_called()

    def it_banks_the_leg_under_the_forward_runs_own_reverse_root(report, collaborators):
        assert collaborators["reverse_command"].call_args.kwargs["reverse_run_root"] == (
            PLACES["reverse_directory"] / RUN.name
        )
        assert report["reverse_root"] == str(PLACES["reverse_directory"] / RUN.name)

    def it_reads_the_reference_from_the_staged_derivations_root(report, collaborators):
        assert collaborators["reverse_command"].call_args.kwargs["staged_derivations_directory"] == STAGED.parent

    def it_reports_the_command_and_its_environment(report):
        assert (report["argv"], report["env"]) == (COMMAND["argv"], COMMAND["env"])

    def it_reports_the_reverse_condition_with_both_suites(report):
        assert report["condition"] == REVERSE_CONDITION

    def it_reports_the_forward_run_and_its_condition(report):
        assert report["forward"] == {"run_id": RUN.name, "condition": FORWARD_CONDITION}

    def it_reports_the_staged_derivation(report):
        assert report["staged"] == str(STAGED)

    def it_carries_the_forward_runs_own_estimate(report):
        assert report["estimate"] == ESTIMATE
