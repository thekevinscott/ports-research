import json
from pathlib import Path


def find_runs(paths: list[Path]) -> list[Path]:
    """Each path as a run directory, or as a directory of runs; only runs whose agent exited 0."""

    def is_run(path: Path) -> bool:
        return (path / "manifest.json").is_file()

    candidates = []
    for path in paths:
        candidates += [path] if is_run(path) else sorted(p for p in path.iterdir() if is_run(p))
    runs = []
    for run in candidates:
        if run not in runs and json.loads((run / "manifest.json").read_text()).get("exit_code") == 0:
            runs.append(run)
    return runs
