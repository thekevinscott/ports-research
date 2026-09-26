import json
from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.load_run import load_run

CONDITION = {
    "name": "source-python_python-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def usage():
    with patch("round_trip_experiment.load_run.transcript_usage", autospec=True) as m:
        m.return_value = {"total_tokens": 4697263, "api_calls": 63}
        yield m


@pytest.fixture
def run(tmp_path: Path) -> Path:
    directory = tmp_path / "20260909T001426Z_1c28aa33"
    directory.mkdir()
    (directory / "manifest.json").write_text(json.dumps({"condition": CONDITION}))
    (directory / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 456517}))
    return directory


def describe_load_run():
    def it_names_the_run_by_its_directory(usage, run):
        assert load_run(run)["run_id"] == "20260909T001426Z_1c28aa33"

    def it_reads_the_forward_condition_from_the_manifest(usage, run):
        assert load_run(run)["condition"] == CONDITION

    def it_estimates_from_the_runs_own_transcript_tokens_and_duration(usage, run):
        assert load_run(run)["estimate"] == {"total_tokens": 4697263, "api_calls": 63, "duration_ms": 456517}

    def it_reads_the_transcript_of_the_given_run(usage, run):
        load_run(run)
        usage.assert_called_once_with(run)

    def it_leaves_the_estimate_empty_when_the_run_never_finished(usage, run):
        usage.return_value = {}
        (run / "result.json").unlink()
        assert load_run(run)["estimate"] == {"total_tokens": None, "api_calls": None, "duration_ms": None}

    def it_fails_without_a_manifest(usage, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_run(tmp_path)
