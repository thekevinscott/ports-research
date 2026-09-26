"""The notebook is the charts' source of truth, so it must stay runnable."""

import subprocess
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "runs.py"


def test_notebook_passes_marimos_static_checks():
    # A duplicated kwarg and a cell-level name collision with src.corpus.REFERENCE both
    # reached main because the unit tests never load the notebook.
    result = subprocess.run(
        ["marimo", "check", str(NOTEBOOK)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr or result.stdout
