import importlib.util
import subprocess
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "fidelity.py"
HEADINGS = [
    "# Judging fidelity: techniques on the table",
    "## Built",
    "## Decided, not built",
    "## Literature only",
    "## Tests as the judge",
]


def rendered_cells() -> list[str]:
    spec = importlib.util.spec_from_file_location("fidelity", NOTEBOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs, _ = module.app.run()
    return [output.text for output in outputs if output is not None]


def describe_fidelity_notebook():
    def it_passes_marimos_static_checks():
        result = subprocess.run(
            ["marimo", "check", str(NOTEBOOK)], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr or result.stdout

    def it_renders_one_markdown_cell_per_section_in_order():
        cells = rendered_cells()
        assert len(cells) == len(HEADINGS)
        for cell, heading in zip(cells, HEADINGS):
            assert heading.lstrip("# ") in cell
