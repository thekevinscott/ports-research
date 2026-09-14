import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from round_trip_experiment.reverse_port_cli import cli

FORWARD_CONDITION = {
    "name": "source-python_python-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}
REPORT = {
    "forward": {"run_id": "20260909T001426Z_1c28aa33", "condition": FORWARD_CONDITION},
    "condition": {
        "source_language": "typescript",
        "include_typescript_tests": True,
        "include_python_tests": True,
        "effort": "high",
        "model": "claude-opus-5",
    },
    "staged": "/cache/staging/20260909T001426Z_1c28aa33/390bf534c55d496b",
    "reverse_root": "/pkg/reverse/20260909T001426Z_1c28aa33",
    "argv": ["uv", "run", "--directory", "/repo/packages/gbnf-experiment", "run-gbnf-experiment"],
    "env": {
        "GBNF_EXPERIMENT_DERIVATIONS_DIRECTORY": "/cache/staging/20260909T001426Z_1c28aa33",
        "GBNF_EXPERIMENT_DATA_DIRECTORY": "/pkg/reverse/20260909T001426Z_1c28aa33",
    },
    "estimate": {"total_tokens": 4697263, "api_calls": 63, "duration_ms": 456517},
}
MANIFEST = {"timestamp": "2026-09-09T02:11:03Z", "forward": REPORT["forward"]}
BANKED = Path("/pkg/reverse/20260909T001426Z_1c28aa33/20260909T021103Z_9f0a1b2c")


@pytest.fixture
def forward_run(tmp_path: Path) -> Path:
    directory = tmp_path / "20260909T001426Z_1c28aa33"
    directory.mkdir()
    return directory


@pytest.fixture
def reverse_run(tmp_path: Path) -> Path:
    directory = tmp_path / "20260909T021103Z_9f0a1b2c"
    directory.mkdir()
    return directory


@pytest.fixture
def reverse_leg():
    with patch("round_trip_experiment.reverse_port_cli.reverse_leg", autospec=True) as m:
        m.return_value = REPORT
        yield m


@pytest.fixture
def load_run():
    with patch("round_trip_experiment.reverse_port_cli.load_run", autospec=True) as m:
        m.return_value = {"run_id": "20260909T001426Z_1c28aa33", "condition": FORWARD_CONDITION, "estimate": {}}
        yield m


@pytest.fixture
def record_forward():
    with patch("round_trip_experiment.reverse_port_cli.record_forward", autospec=True) as m:
        m.return_value = MANIFEST
        yield m


@pytest.fixture
def banked():
    with patch("round_trip_experiment.reverse_port_cli.reverse_run_directory", autospec=True) as m:
        m.return_value = BANKED
        yield m


@pytest.fixture
def launch():
    with patch("round_trip_experiment.reverse_port_cli.subprocess.run", autospec=True) as m:
        m.return_value = CompletedProcess(REPORT["argv"], 0)
        yield m


@pytest.fixture
def places():
    with (
        patch("round_trip_experiment.reverse_port_cli.derivation_cache_key", "390bf534c55d496b"),
        patch("round_trip_experiment.reverse_port_cli.gbnf_settings") as gbnf,
        patch("round_trip_experiment.reverse_port_cli.settings") as own,
        patch(
            "round_trip_experiment.reverse_port_cli.GBNF_EXPERIMENT_ROOT",
            Path("/repo/packages/gbnf-experiment"),
        ),
    ):
        gbnf.derivations_directory = Path("/cache/gbnf-experiment/derivations")
        own.staging_directory = Path("/cache/staging")
        own.reverse_directory = Path("/pkg/reverse")
        yield


@pytest.fixture
def wired(reverse_leg, load_run, record_forward, banked, launch, places):
    return None


def invoke(*args):
    return CliRunner().invoke(cli, list(args))


def describe_stage():
    def it_requires_a_run(wired):
        result = invoke("stage")
        assert result.exit_code != 0
        assert "--run" in result.output

    def it_rejects_a_run_that_does_not_exist(wired, tmp_path):
        result = invoke("stage", "--run", str(tmp_path / "nowhere"))
        assert result.exit_code != 0

    def it_stages_the_leg_with_the_configured_places(wired, reverse_leg, forward_run):
        invoke("stage", "--run", str(forward_run))
        assert reverse_leg.call_args.args == (forward_run,)
        assert reverse_leg.call_args.kwargs == {
            "derivation_cache_key": "390bf534c55d496b",
            "derivations_directory": Path("/cache/gbnf-experiment/derivations"),
            "gbnf_experiment_directory": Path("/repo/packages/gbnf-experiment"),
            "staging_directory": Path("/cache/staging"),
            "reverse_directory": Path("/pkg/reverse"),
        }

    def it_prints_the_command_and_the_estimate(wired, forward_run):
        result = invoke("stage", "--run", str(forward_run))
        assert json.loads(result.output) == REPORT
        assert result.exit_code == 0

    def it_launches_nothing(wired, launch, forward_run):
        invoke("stage", "--run", str(forward_run))
        launch.assert_not_called()

    def it_renders_errors_as_click_errors(wired, reverse_leg, forward_run):
        reverse_leg.side_effect = FileNotFoundError("ported_implementation")
        result = invoke("stage", "--run", str(forward_run))
        assert result.exit_code != 0
        assert "ported_implementation" in result.output


def describe_record():
    def it_requires_both_runs(wired, reverse_run):
        result = invoke("record", "--run", str(reverse_run))
        assert result.exit_code != 0
        assert "--forward" in result.output

    def it_amends_the_reverse_manifest_with_the_forward_run(wired, record_forward, reverse_run, forward_run):
        invoke("record", "--run", str(reverse_run), "--forward", str(forward_run))
        record_forward.assert_called_once_with(
            reverse_run,
            run_id="20260909T001426Z_1c28aa33",
            condition=FORWARD_CONDITION,
        )

    def it_reads_the_forward_condition_from_the_forward_run(wired, load_run, reverse_run, forward_run):
        invoke("record", "--run", str(reverse_run), "--forward", str(forward_run))
        load_run.assert_called_once_with(forward_run)

    def it_prints_the_amended_manifest(wired, reverse_run, forward_run):
        result = invoke("record", "--run", str(reverse_run), "--forward", str(forward_run))
        assert json.loads(result.output) == MANIFEST
        assert result.exit_code == 0

    def it_renders_errors_as_click_errors(wired, record_forward, reverse_run, forward_run):
        record_forward.side_effect = FileNotFoundError("manifest.json")
        result = invoke("record", "--run", str(reverse_run), "--forward", str(forward_run))
        assert result.exit_code != 0
        assert "manifest.json" in result.output


def describe_run():
    def it_stages_the_leg_before_launching(wired, reverse_leg, forward_run):
        invoke("run", "--run", str(forward_run))
        reverse_leg.assert_called_once()

    def it_launches_run_gbnf_experiment_with_the_staged_environment(wired, launch, forward_run):
        invoke("run", "--run", str(forward_run))
        assert launch.call_args.args == (REPORT["argv"],)
        assert REPORT["env"].items() <= launch.call_args.kwargs["env"].items()

    def it_refuses_to_launch_when_the_staged_derivation_is_incomplete(wired, reverse_leg, launch, forward_run):
        reverse_leg.side_effect = ValueError("staged derivation is incomplete, refusing to launch")
        result = invoke("run", "--run", str(forward_run))
        assert result.exit_code != 0
        assert "refusing to launch" in result.output
        launch.assert_not_called()

    def it_records_the_forward_run_on_the_leg_it_banked(wired, record_forward, forward_run):
        invoke("run", "--run", str(forward_run))
        record_forward.assert_called_once_with(
            BANKED,
            run_id="20260909T001426Z_1c28aa33",
            condition=FORWARD_CONDITION,
        )

    def it_records_a_failed_leg_that_still_banked_a_directory(wired, launch, record_forward, forward_run):
        launch.return_value = CompletedProcess(REPORT["argv"], 1)
        result = invoke("run", "--run", str(forward_run))
        record_forward.assert_called_once()
        assert result.exit_code == 1

    def it_records_nothing_when_the_leg_banked_no_directory(wired, banked, record_forward, forward_run):
        banked.return_value = None
        result = invoke("run", "--run", str(forward_run))
        record_forward.assert_not_called()
        assert json.loads(result.output)["run_directory"] is None

    def it_prints_the_leg_it_banked(wired, forward_run):
        result = invoke("run", "--run", str(forward_run))
        assert json.loads(result.output) == {**REPORT, "run_directory": str(BANKED), "returncode": 0}
        assert result.exit_code == 0
