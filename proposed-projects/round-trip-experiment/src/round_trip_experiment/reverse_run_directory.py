from pathlib import Path


def reverse_run_directory(root: Path, *, before: set[str]) -> Path | None:
    """The harness prints its run directory only when the run succeeds, so the leg is found
    by diffing its own output root instead — a failed leg is still banked and still joins
    back to the forward run.
    """
    if not root.is_dir():
        return None
    added = sorted(path for path in root.iterdir() if path.is_dir() and path.name not in before)
    return added[-1] if added else None
