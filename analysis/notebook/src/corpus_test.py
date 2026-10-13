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


def write_matrix(path, *run_ids):
    # The driver records each run's directory where it ran, often another worktree.
    path.write_text(
        "".join(json.dumps({"run_directory": f"/elsewhere/data/runs/{run_id}", "exit_code": 0}) + "\n" for run_id in run_ids)
        + json.dumps({"run_directory": None, "exit_code": 1}) + "\n"
    )


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

    def it_keeps_only_the_v2_runs_the_named_matrices_list(tmp_path):
        write_v2_run(tmp_path / "study")
        write_v2_run(tmp_path / "pilot")
        write_matrix(tmp_path / "matrix-study.jsonl", "study")
        runs = runs_under(tmp_path, runs_table(), matrices=["matrix-study.jsonl"])
        assert [run["run_id"] for run in runs] == ["study"]

    def it_keeps_v1_runs_whatever_the_matrices(tmp_path):
        write_v1_run(tmp_path / "v1")
        write_v2_run(tmp_path / "pilot")
        write_matrix(tmp_path / "matrix-study.jsonl")
        runs = runs_under(tmp_path, runs_table(), matrices=["matrix-study.jsonl"])
        assert [run["run_id"] for run in runs] == ["v1"]

    def it_reads_no_matrix_under_a_root_without_v2_runs(tmp_path):
        # The reverse-port scan holds V1 runs only and none of the runs directory's matrix logs.
        write_v1_run(tmp_path / "v1")
        runs = runs_under(tmp_path, runs_table(), matrices=["matrix-study.jsonl"])
        assert [run["run_id"] for run in runs] == ["v1"]

    def it_reads_the_matrices_from_PORTS_MATRICES(tmp_path, monkeypatch):
        write_v2_run(tmp_path / "study")
        write_v2_run(tmp_path / "pilot")
        write_v2_run(tmp_path / "refill")
        write_matrix(tmp_path / "matrix-a.jsonl", "study")
        write_matrix(tmp_path / "matrix-b.jsonl", "refill")
        monkeypatch.setenv("PORTS_MATRICES", "matrix-a.jsonl, matrix-b.jsonl")
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table())] == ["refill", "study"]
        assert [codebase.run_id for codebase in codebases_under(tmp_path, runs_table())] == ["refill", "study"]

    def it_keeps_every_run_without_PORTS_MATRICES(tmp_path, monkeypatch):
        monkeypatch.delenv("PORTS_MATRICES", raising=False)
        write_v2_run(tmp_path / "study")
        write_v2_run(tmp_path / "pilot")
        assert [run["run_id"] for run in runs_under(tmp_path, runs_table())] == ["pilot", "study"]
