import json
from pathlib import Path


def matrix_run_ids(root: Path, matrices: list[str]) -> set[str]:
    """Run ids a study driver's matrix logs record; a log names each run's directory where it ran, so the id is its last part."""
    ids = set()
    for matrix in matrices:
        for line in (root / matrix).read_text().splitlines():
            if line.strip() and (directory := json.loads(line).get("run_directory")):
                ids.add(Path(directory).name)
    return ids
