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


def write_v2_run(run_dir, exit_code=0, study="v2-test-configurations"):
    (run_dir / "ported_implementation" / "src").mkdir(parents=True)
    (run_dir / "ported_implementation" / "src" / "index.ts").write_text("export default 1;\n")
    manifest = {
        "timestamp": "2026-10-12T09:49:53Z",
        "completed_at": "2026-10-12T09:56:41Z",
        "exit_code": exit_code,
        "study": study,
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
        write_v2_run(tmp_path / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table())
        assert codebase.language == "javascript"
        assert codebase.file_count == 1

    def it_measures_a_javascript_port_against_the_pinned_javascript_reference(tmp_path, pinned_reference):
        write_v2_run(tmp_path / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table())
        pinned_reference.assert_called_once_with()
        assert codebase.reference == REFERENCE_CHECKOUT / "packages" / "gbnf" / "javascript"

    def it_leaves_the_javascript_build_tooling_out_as_for_typescript(tmp_path, pinned_reference):
        write_v2_run(tmp_path / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table())
        assert {"builder", "dev"} <= set(codebase.exclude)


def describe_runs_under():
    def it_lists_exit_zero_runs(tmp_path):
        write_v2_run(tmp_path / "ok")
        write_v2_run(tmp_path / "killed", exit_code=137)
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table())] == ["ok"]

    def it_lists_killed_runs_when_asked(tmp_path):
        write_v2_run(tmp_path / "ok")
        write_v2_run(tmp_path / "killed", exit_code=137)
        runs = runs_under(tmp_path, runs_table(), include_nonzero_exit=True)
        assert [(run["run_id"], run["exit_code"]) for run in runs] == [("killed", 137), ("ok", 0)]

    def it_keeps_only_the_v2_runs_of_the_named_study(tmp_path):
        write_v2_run(tmp_path / "effort", study="v2-model-effort")
        write_v2_run(tmp_path / "tests", study="v2-test-configurations")
        runs = runs_under(tmp_path, runs_table(), study="v2-model-effort")
        assert [run["run_id"] for run in runs] == ["effort"]

    def it_keeps_v1_runs_whatever_the_study(tmp_path):
        write_v1_run(tmp_path / "v1")
        write_v2_run(tmp_path / "effort", study="v2-model-effort")
        runs = runs_under(tmp_path, runs_table(), study="v2-test-configurations")
        assert [run["run_id"] for run in runs] == ["v1"]

    def it_drops_a_v2_run_whose_manifest_names_no_study(tmp_path):
        write_v2_run(tmp_path / "pilot", study=None)
        assert runs_under(tmp_path, runs_table()) == []

    def it_reads_the_study_from_PORTS_STUDY(tmp_path, monkeypatch, pinned_reference):
        write_v2_run(tmp_path / "effort", study="v2-model-effort")
        write_v2_run(tmp_path / "tests", study="v2-test-configurations")
        monkeypatch.setenv("PORTS_STUDY", "v2-model-effort")
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table())] == ["effort"]
        assert [codebase.run_id for codebase in codebases_under(tmp_path, runs_table())] == ["effort"]

    def it_reads_the_test_configurations_study_without_PORTS_STUDY(tmp_path, monkeypatch):
        monkeypatch.delenv("PORTS_STUDY", raising=False)
        write_v2_run(tmp_path / "effort", study="v2-model-effort")
        write_v2_run(tmp_path / "tests", study="v2-test-configurations")
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table())] == ["tests"]
