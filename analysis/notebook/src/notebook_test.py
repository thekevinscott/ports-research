"""The notebook is the charts' source of truth, so it must stay runnable."""

import ast
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


SOURCE = NOTEBOOK.read_text()
EMBEDDING_EXPORT = NOTEBOOK.parent / "export_embedding_pairs.py"


def assigned(name: str, source: str = SOURCE) -> str:
    for node in ast.walk(ast.parse(source)):
        targets = getattr(node, "targets", [])
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.unparse(node.value)
    raise AssertionError(f"{name} is not assigned")


def test_the_v1_sections_measure_v1_runs_only():
    assert "if not is_v2(codebase.run)" in assigned("codebases")


def test_the_embedding_pair_export_reads_v1_runs_only():
    assert "if not is_v2(codebase.run)" in EMBEDDING_EXPORT.read_text()
