import json

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


def describe_codebases_under():
    def it_builds_a_codebase_for_a_javascript_port(tmp_path):
        write_v2_run(tmp_path / "20261012T094953Z_370ab98a")
        (codebase,) = codebases_under(tmp_path, runs_table())
        assert codebase.language == "javascript"
        assert codebase.file_count == 1


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
