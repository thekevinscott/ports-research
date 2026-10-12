import json
from pathlib import Path

from dirsql import Table
from gbnf_experiment.transcript_usage import transcript_usage

RUNS_COLUMNS = {
    "run_id": "TEXT PRIMARY KEY",
    "run_dir": "TEXT",
    "timestamp": "TEXT",
    "completed_at": "TEXT",
    "source_language": "TEXT",
    "target_language": "TEXT",
    # V1 runs carry the two suite flags, V2 runs the three; a row has one set, the other null.
    "include_python_tests": "INTEGER",
    "include_typescript_tests": "INTEGER",
    "include_unit_tests": "INTEGER",
    "include_source_integration_tests": "INTEGER",
    "include_target_integration_tests": "INTEGER",
    "exit_code": "INTEGER",
    "model": "TEXT",
    "effort": "TEXT",
    "error": "TEXT",
    "is_error": "INTEGER",
    "total_tokens": "INTEGER",
    "api_calls": "INTEGER",
    "duration_ms": "INTEGER",
    "harness_commit": "TEXT",
}
REVERSE_RUNS_COLUMNS = {
    **RUNS_COLUMNS,
    "forward_run_id": "TEXT",
    "forward_source_language": "TEXT",
    "forward_target_language": "TEXT",
    "forward_include_python_tests": "INTEGER",
    "forward_include_typescript_tests": "INTEGER",
}
COMPLETED = "is_error = 0 AND error IS NULL AND completed_at IS NOT NULL"
# V1 manifests carry no exit code.
EXIT_ZERO = "COALESCE(exit_code, 0) = 0"
V1_FLAGS = ["include_python_tests", "include_typescript_tests"]
V2_FLAGS = [
    "include_unit_tests",
    "include_source_integration_tests",
    "include_target_integration_tests",
]


def _ddl(name: str, columns: dict[str, str]) -> str:
    return f"CREATE TABLE {name} ({', '.join(f'{c} {t}' for c, t in columns.items())})"


def _row(manifest_path: Path, manifest: dict) -> dict:
    result_path = manifest_path.parent / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    tokens = transcript_usage(manifest_path.parent)
    condition = manifest["condition"]
    return {
        "run_id": manifest_path.parent.name,
        "run_dir": str(manifest_path.parent),
        "timestamp": manifest["timestamp"],
        "completed_at": manifest.get("completed_at"),
        "source_language": condition["source_language"],
        "target_language": condition["target_language"],
        **{flag: condition.get(flag) for flag in (*V1_FLAGS, *V2_FLAGS)},
        "exit_code": manifest.get("exit_code"),
        "model": condition["model"],
        "effort": condition["effort"],
        "error": manifest.get("error"),
        "is_error": result.get("is_error"),
        "total_tokens": tokens.get("total_tokens"),
        "api_calls": tokens.get("api_calls"),
        "duration_ms": result.get("duration_ms"),
        "harness_commit": manifest["harness"]["commit"],
    }


def run_rows(path: str) -> list[dict]:
    manifest_path = Path(path)
    return [_row(manifest_path, json.loads(manifest_path.read_text()))]


def reverse_run_rows(path: str) -> list[dict]:
    manifest_path = Path(path)
    manifest = json.loads(manifest_path.read_text())
    forward = manifest["forward"]
    condition = forward["condition"]
    return [
        {
            **_row(manifest_path, manifest),
            "forward_run_id": forward["run_id"],
            "forward_source_language": condition["source_language"],
            "forward_target_language": condition["target_language"],
            "forward_include_python_tests": condition["include_python_tests"],
            "forward_include_typescript_tests": condition["include_typescript_tests"],
        }
    ]


def runs_table() -> Table:
    return Table(
        name="runs",
        ddl=_ddl("runs", RUNS_COLUMNS),
        glob="*/manifest.json",
        on_file=run_rows,
    )


def reverse_runs_table() -> Table:
    # reverse/<forward run id>/<reverse run id>/, one directory deeper than a forward run.
    return Table(
        name="reverse_runs",
        ddl=_ddl("reverse_runs", REVERSE_RUNS_COLUMNS),
        glob="*/*/manifest.json",
        on_file=reverse_run_rows,
    )


def is_v2(run: dict) -> bool:
    return run["include_unit_tests"] is not None


def completed_runs(db, table: str, *, include_nonzero_exit: bool = False) -> list[dict]:
    where = COMPLETED if include_nonzero_exit else f"{COMPLETED} AND {EXIT_ZERO}"
    return db.query(f"SELECT * FROM {table} WHERE {where} ORDER BY run_id")
