import json
from unittest.mock import patch

import pytest

from src.Codebase import REFERENCE_CHECKOUT
from src.corpus import codebases_under, runs_under
from src.run_table import runs_table

V2_CONDITION = {
    "name": "source-python_unit-tests_effort-medium_model-claude-opus-5-5",
    "source_language": "python",
    "target_language": "javascript",
    "include_unit_tests": True,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}


EXPERIMENT = "v2-tests-configuration"


def write_v2_run(run_dir, exit_code=0):
    (run_dir / "ported_implementation" / "src").mkdir(parents=True)
    (run_dir / "ported_implementation" / "src" / "index.ts").write_text("export default 1;\n")
    manifest = {
        "timestamp": "2026-10-12T09:49:53Z",
        "completed_at": "2026-10-12T09:56:41Z",
        "exit_code": exit_code,
        "condition": V2_CONDITION,
        "harness": {"commit": "87066d86c7b5986f693a3cbea4350f4ec11fec4d", "dirty": False},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    # A run killed with exit 137 never writes its result.
    if exit_code != 137:
        (run_dir / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 1}))


V1_CONDITION = {
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}


def write_v1_run(run_dir):
    run_dir.mkdir(parents=True)
    manifest = {
        "timestamp": "2026-09-08T23:42:47Z",
        "completed_at": "2026-09-08T23:50:00Z",
        "condition": V1_CONDITION,
        "harness": {"commit": "353d5b3", "dirty": False},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 1}))


@pytest.fixture
def pinned_reference():
    with patch("src.corpus.pinned_reference", autospec=True) as m:
        m.return_value = REFERENCE_CHECKOUT
        yield m


def describe_codebases_under():
    def it_builds_a_codebase_for_a_javascript_port(tmp_path, pinned_reference):
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table(), EXPERIMENT)
        assert codebase.language == "javascript"
        assert codebase.file_count == 1

    def it_measures_a_javascript_port_against_the_pinned_javascript_reference(tmp_path, pinned_reference):
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table(), EXPERIMENT)
        pinned_reference.assert_called_once_with()
        assert codebase.reference == REFERENCE_CHECKOUT / "packages" / "gbnf" / "javascript"

    def it_leaves_the_javascript_build_tooling_out_as_for_typescript(tmp_path, pinned_reference):
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table(), EXPERIMENT)
        assert {"builder", "dev"} <= set(codebase.exclude)

    def it_keeps_only_the_v2_codebases_of_the_named_experiment(tmp_path, pinned_reference):
        write_v2_run(tmp_path / "v2-models-effort" / "runs" / "effort")
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "tests")
        assert [codebase.run_id for codebase in codebases_under(tmp_path, runs_table(), "v2-models-effort")] == ["effort"]


def describe_runs_under():
    def it_lists_exit_zero_runs(tmp_path):
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "ok")
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "killed", exit_code=137)
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table(), EXPERIMENT)] == ["ok"]

    def it_lists_killed_runs_when_asked(tmp_path):
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "ok")
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "killed", exit_code=137)
        runs = runs_under(tmp_path, runs_table(), EXPERIMENT, include_nonzero_exit=True)
        assert [(run["run_id"], run["exit_code"]) for run in runs] == [("killed", 137), ("ok", 0)]

    def it_keeps_only_the_v2_runs_of_the_named_experiment(tmp_path):
        write_v2_run(tmp_path / "v2-models-effort" / "runs" / "effort")
        write_v2_run(tmp_path / EXPERIMENT / "runs" / "tests")
        runs = runs_under(tmp_path, runs_table(), "v2-models-effort")
        assert [run["run_id"] for run in runs] == ["effort"]

    def it_keeps_v1_runs_whatever_the_experiment(tmp_path):
        write_v1_run(tmp_path / "v2-models-effort" / "runs" / "v1")
        write_v2_run(tmp_path / "v2-models-effort" / "runs" / "effort")
        runs = runs_under(tmp_path, runs_table(), EXPERIMENT)
        assert [run["run_id"] for run in runs] == ["v1"]
