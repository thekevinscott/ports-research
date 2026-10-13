import json
from pathlib import Path

from dirsql._dirsql import DirSQL

from src.run_table import (
    completed_runs,
    reverse_run_rows,
    reverse_runs_table,
    run_rows,
    runs_table,
)

FORWARD_CONDITION = {
    "name": "source-python_typescript-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": False,
    "include_typescript_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}
REVERSE_CONDITION = {
    "name": "source-typescript_typescript-tests_python-tests_effort-high_model-claude-opus-5",
    "source_language": "typescript",
    "target_language": "python",
    "include_python_tests": True,
    "include_typescript_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}
FORWARD = {"run_id": "20260909T004354Z_a47a3057", "condition": FORWARD_CONDITION}
USAGE = {
    "input_tokens": 100,
    "cache_creation_input_tokens": 20,
    "cache_read_input_tokens": 3,
    "output_tokens": 7,
}


def write_run(
    run_dir: Path,
    condition: dict,
    *,
    forward: dict | None = None,
    completed: bool = True,
    is_error: bool = False,
) -> Path:
    run_dir.mkdir(parents=True)
    manifest = {
        "timestamp": "2026-09-10T04:41:03Z",
        "condition": condition,
        "harness": {"commit": "a49991e28b75a32320c35498db63515d44c566e9", "dirty": False},
    }
    if completed:
        manifest["completed_at"] = "2026-09-10T04:50:25Z"
    if forward is not None:
        manifest["forward"] = forward
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "result.json").write_text(json.dumps({"is_error": is_error, "duration_ms": 560157}))
    transcript = run_dir / "transcript"
    transcript.mkdir()
    (transcript / "session.jsonl").write_text(
        "\n".join(
            json.dumps({"type": "assistant", "message": {"id": message_id, "usage": USAGE}})
            for message_id in ("msg_1", "msg_1", "msg_2")
        )
    )
    return run_dir


def describe_run_rows():
    def it_reads_the_condition_and_the_run_directory(tmp_path):
        run_dir = write_run(tmp_path / "20260909T004354Z_a47a3057", FORWARD_CONDITION)
        (row,) = run_rows(str(run_dir / "manifest.json"))
        assert row["run_id"] == "20260909T004354Z_a47a3057"
        assert row["run_dir"] == str(run_dir)
        assert row["source_language"] == "python"
        assert row["target_language"] == "typescript"
        assert row["include_python_tests"] is False
        assert row["completed_at"] == "2026-09-10T04:50:25Z"
        assert row["error"] is None

    def it_reads_the_result_and_the_transcript(tmp_path):
        run_dir = write_run(tmp_path / "run", FORWARD_CONDITION)
        (row,) = run_rows(str(run_dir / "manifest.json"))
        assert row["is_error"] is False
        assert row["duration_ms"] == 560157
        assert row["total_tokens"] == 260
        assert row["api_calls"] == 2

    def it_carries_no_forward_columns(tmp_path):
        run_dir = write_run(tmp_path / "run", FORWARD_CONDITION)
        (row,) = run_rows(str(run_dir / "manifest.json"))
        assert "forward_run_id" not in row


V2_CONDITION = {
    "source_language": "python",
    "target_language": "javascript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}


def v2_row(tmp_path, **condition):
    run_dir = write_run(tmp_path / "run", {**V2_CONDITION, **condition})
    (row,) = run_rows(str(run_dir / "manifest.json"))
    return row


def describe_v2_run_rows():
    def it_loads_a_javascript_target_as_typescript(tmp_path):
        row = v2_row(tmp_path)
        assert row["source_language"] == "python"
        assert row["target_language"] == "typescript"

    def it_loads_a_javascript_source_as_typescript(tmp_path):
        row = v2_row(tmp_path, source_language="javascript", target_language="python")
        assert row["source_language"] == "typescript"
        assert row["target_language"] == "python"

    def it_sets_no_suite_flag_when_no_suite_is_included(tmp_path):
        row = v2_row(tmp_path)
        assert row["include_python_tests"] is False
        assert row["include_typescript_tests"] is False

    def it_counts_the_unit_suite_in_the_source_language(tmp_path):
        row = v2_row(tmp_path, include_unit_tests=True)
        assert row["include_python_tests"] is True
        assert row["include_typescript_tests"] is False

    def it_counts_the_source_integration_suite_in_the_source_language(tmp_path):
        row = v2_row(
            tmp_path,
            source_language="javascript",
            target_language="python",
            include_source_integration_tests=True,
        )
        assert row["include_python_tests"] is False
        assert row["include_typescript_tests"] is True

    def it_counts_the_target_integration_suite_in_the_target_language(tmp_path):
        row = v2_row(tmp_path, include_target_integration_tests=True)
        assert row["include_python_tests"] is False
        assert row["include_typescript_tests"] is True

    def it_sets_both_flags_when_suites_cover_both_languages(tmp_path):
        row = v2_row(tmp_path, include_unit_tests=True, include_target_integration_tests=True)
        assert row["include_python_tests"] is True
        assert row["include_typescript_tests"] is True

    def it_reads_model_and_effort(tmp_path):
        row = v2_row(tmp_path)
        assert row["model"] == "claude-opus-5-5"
        assert row["effort"] == "medium"


def describe_reverse_run_rows():
    def it_reads_the_reverse_condition(tmp_path):
        run_dir = write_run(tmp_path / "fwd" / "rev", REVERSE_CONDITION, forward=FORWARD)
        (row,) = reverse_run_rows(str(run_dir / "manifest.json"))
        assert row["run_id"] == "rev"
        assert row["source_language"] == "typescript"
        assert row["target_language"] == "python"
        assert row["include_python_tests"] is True
        assert row["include_typescript_tests"] is True

    def it_reads_the_forward_condition(tmp_path):
        run_dir = write_run(tmp_path / "fwd" / "rev", REVERSE_CONDITION, forward=FORWARD)
        (row,) = reverse_run_rows(str(run_dir / "manifest.json"))
        assert row["forward_run_id"] == "20260909T004354Z_a47a3057"
        assert row["forward_source_language"] == "python"
        assert row["forward_target_language"] == "typescript"
        assert row["forward_include_python_tests"] is False
        assert row["forward_include_typescript_tests"] is True


def describe_tables():
    def it_globs_forward_runs_one_level_under_the_root():
        assert runs_table().glob == "*/manifest.json"

    def it_globs_reverse_runs_two_levels_under_the_root():
        assert reverse_runs_table().glob == "*/*/manifest.json"


def describe_completed_runs():
    def it_keeps_only_completed_error_free_runs(tmp_path):
        write_run(tmp_path / "f1" / "r1", REVERSE_CONDITION, forward=FORWARD)
        write_run(tmp_path / "f2" / "r2", REVERSE_CONDITION, forward=FORWARD, completed=False)
        write_run(tmp_path / "f3" / "r3", REVERSE_CONDITION, forward=FORWARD, is_error=True)
        db = DirSQL(str(tmp_path), tables=[reverse_runs_table()])
        assert [row["run_id"] for row in completed_runs(db, "reverse_runs")] == ["r1"]

    def it_carries_the_forward_run_id_through_the_query(tmp_path):
        write_run(tmp_path / "20260909T004354Z_a47a3057" / "r1", REVERSE_CONDITION, forward=FORWARD)
        db = DirSQL(str(tmp_path), tables=[reverse_runs_table()])
        (row,) = completed_runs(db, "reverse_runs")
        assert row["forward_run_id"] == "20260909T004354Z_a47a3057"
        assert row["forward_include_typescript_tests"] == 1

    def it_picks_up_a_reverse_run_written_after_an_earlier_scan(tmp_path):
        write_run(tmp_path / "f1" / "r1", REVERSE_CONDITION, forward=FORWARD)
        first = DirSQL(str(tmp_path), tables=[reverse_runs_table()])
        assert [row["run_id"] for row in completed_runs(first, "reverse_runs")] == ["r1"]
        write_run(tmp_path / "f2" / "r2", REVERSE_CONDITION, forward=FORWARD)
        later = DirSQL(str(tmp_path), tables=[reverse_runs_table()])
        assert [row["run_id"] for row in completed_runs(later, "reverse_runs")] == ["r1", "r2"]
