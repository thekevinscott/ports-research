"""The model and effort study: four models at every effort level, unit and source integration tests, both directions.

40 cells a round, 12 rounds, 480 runs. Flags and stop rules are study.py's.
Runs already completed under --output count toward --n, so a rerun skips them.
"""

import json
from collections import Counter
from itertools import product
from pathlib import Path

from dirsql import Table
# The package's DirSQL is the async wrapper; the notebook uses the sync binding the same way.
from dirsql._dirsql import DirSQL

import study
from study import SOURCE_LANGUAGES, cell_key

STUDY = "v2-model-effort"
MODELS = ("claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
TESTS = {
    "include_unit_tests": True,
    "include_source_integration_tests": True,
    "include_target_integration_tests": False,
}
COMPLETED = f"study = '{STUDY}' AND exit_code = 0 AND is_error = 0 AND error IS NULL AND completed_at IS NOT NULL"


def cells() -> list[dict]:
    return [
        {"source_language": source_language, **TESTS, "model": model, "effort": effort}
        for source_language, model, effort in product(SOURCE_LANGUAGES, MODELS, EFFORTS)
    ]


def run_rows(path: str) -> list[dict]:
    manifest_path = Path(path)
    manifest = json.loads(manifest_path.read_text())
    result_path = manifest_path.parent / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    condition = manifest.get("condition", {})
    return [
        {
            "run_id": manifest_path.parent.name,
            "study": manifest.get("study"),
            "completed_at": manifest.get("completed_at"),
            "exit_code": manifest.get("exit_code"),
            "error": manifest.get("error"),
            "is_error": result.get("is_error"),
            "source_language": condition.get("source_language"),
            "model": condition.get("model"),
            "effort": condition.get("effort"),
            **{flag: condition.get(flag) for flag in TESTS},
        }
    ]


RUNS = Table(
    name="runs",
    ddl=(
        "CREATE TABLE runs (run_id TEXT PRIMARY KEY, study TEXT, completed_at TEXT, exit_code INTEGER, error TEXT,"
        " is_error INTEGER, source_language TEXT, model TEXT, effort TEXT,"
        " include_unit_tests INTEGER, include_source_integration_tests INTEGER, include_target_integration_tests INTEGER)"
    ),
    glob="*/manifest.json",
    on_file=run_rows,
)


def completed_runs(output: Path) -> list[dict]:
    if not output.is_dir():
        return []
    return DirSQL(str(output), tables=[RUNS], no_ignore=True).query(f"SELECT * FROM runs WHERE {COMPLETED}")


def prior_successes(output: Path) -> Counter:
    return Counter(
        cell_key(
            {
                "source_language": run["source_language"],
                **{flag: bool(run[flag]) for flag in TESTS},
                "model": run["model"],
                "effort": run["effort"],
            }
        )
        for run in completed_runs(output)
    )


def main(argv: list[str] | None = None) -> None:
    args = study.argument_parser(__doc__).parse_args(argv)
    study.main(STUDY, cells(), args, prior=prior_successes(args.output))


if __name__ == "__main__":
    main()
