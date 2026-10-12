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


def test_the_behavior_section_measures_v2_runs_only():
    assert "if is_v2(codebase.run)" in assigned("v2_codebases")


V2_FLAG_NAMES = [
    "include_unit_tests",
    "include_source_integration_tests",
    "include_target_integration_tests",
]
CONFUSION = {
    reference: {port: 0 for port in ("accept", "reject", "error", "crash")}
    for reference in ("accept", "reject", "error", "crash")
}


def definitions(*names: str) -> dict:
    """The named constants and functions from runs.py, run outside marimo."""
    import altair as alt
    import polars as pl

    nodes = [
        node
        for node in ast.walk(ast.parse(SOURCE))
        if (isinstance(node, ast.FunctionDef) and node.name in names)
        or (
            isinstance(node, ast.Assign)
            and any(getattr(target, "id", None) in names for target in node.targets)
        )
    ]
    # Constants first: a function reads them when it runs, a constant when it is defined.
    nodes.sort(key=lambda node: isinstance(node, ast.FunctionDef))
    namespace = {"alt": alt, "pl": pl, "V2_FLAGS": V2_FLAG_NAMES}
    module = ast.Module(body=nodes, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(NOTEBOOK), "exec"), namespace)
    return namespace


CHART_NAMES = (
    "INK",
    "TICK_SIZE",
    "BAND_PADDING",
    "DOT_STEP",
    "BAND_FILL",
    "TEST_AXIS_TITLE",
    "V2_CONDITIONS",
    "BEHAVIOR_LEAD",
    "BEHAVIOR_PANEL_WIDTH",
    "BEHAVIOR_SOURCES",
    "panel_title",
    "median_tick",
    "fan_out",
    "dot_offset",
    "with_v2_conditions",
    "behavior_title",
    "behavior_chart",
    "behavior_runs",
)


def v2_row(run_id, source, flags, agreement, note=None):
    return {
        "run_id": run_id,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        **dict(zip(V2_FLAG_NAMES, flags)),
        "behavior_agreement_pct": agreement,
        "reference_accept_port_crash": 0,
        "behavior_note": note,
    }


V2_RUNS = [
    v2_row("a", "python", (0, 1, 1), 99.0),
    v2_row("b", "python", (0, 1, 1), 97.0),
    v2_row("c", "python", (1, 1, 1), 96.0),
    v2_row("d", "javascript", (0, 0, 0), 0.0, "every pair crashed: no src/index.ts"),
]


def test_v2_conditions_label_every_combination_of_the_three_flags_once():
    labels = ast.literal_eval(assigned("V2_CONDITIONS"))
    assert len({label for label, *_ in labels}) == 8
    assert {tuple(flags) for _, *flags in labels} == {
        (unit, source, target)
        for unit in (False, True)
        for source in (False, True)
        for target in (False, True)
    }
    assert labels[0] == ("none", False, False, False)
    assert labels[-1] == ("all", True, True, True)


def test_a_v2_run_carries_agreement_every_confusion_count_and_a_note():
    from types import SimpleNamespace

    behavior_columns = definitions("behavior_columns")["behavior_columns"]
    codebase = SimpleNamespace(
        behavior_agreement_pct=75.0, behavior_confusion=CONFUSION, behavior_note=None
    )
    columns = behavior_columns(codebase)
    assert columns["behavior_agreement_pct"] == 75.0
    assert columns["behavior_note"] is None
    assert len([column for column in columns if column.startswith("reference_")]) == 16
    assert "reference_accept_port_crash" in columns


def test_the_behavior_chart_draws_a_dot_per_run_and_a_median_tick_per_condition():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    spec = namespace["behavior_chart"](pl.DataFrame(V2_RUNS)).to_dict()
    assert spec["title"]["text"] == "Held-out behavior agreement with the reference (%)"
    panels = spec["concat"]
    assert [panel["title"]["text"] for panel in panels] == [
        "python → javascript",
        "javascript → python",
    ]
    marks = [layer["mark"]["type"] for layer in panels[0]["layer"]]
    assert marks == ["tick", "point"]
    assert panels[0]["layer"][0]["encoding"]["y"]["field"] == "value"
    assert panels[0]["layer"][0]["encoding"]["y"]["aggregate"] == "median"
    x = panels[0]["layer"][1]["encoding"]["x"]
    assert x["title"] == "test inclusion"
    assert x["scale"]["domain"] == [label for label, *_ in namespace["V2_CONDITIONS"]]
    datasets = spec["datasets"]
    assert len(datasets[panels[0]["data"]["name"]]) == 3
    assert len(datasets[panels[1]["data"]["name"]]) == 1


def test_the_behavior_chart_titles_a_confusion_count_in_prose():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    spec = namespace["behavior_chart"](
        pl.DataFrame(V2_RUNS), "reference_accept_port_crash"
    ).to_dict()
    assert spec["title"]["text"] == "Pairs the reference accepts and the port crashes on"


def test_the_behavior_run_table_shows_the_note_of_a_port_that_never_loaded():
    import polars as pl

    runs = definitions(*CHART_NAMES)["behavior_runs"](pl.DataFrame(V2_RUNS))
    row = runs.filter(pl.col("run_id") == "d").row(0, named=True)
    assert row["condition"] == "none"
    assert row["behavior_agreement_pct"] == 0.0
    assert row["behavior_note"] == "every pair crashed: no src/index.ts"


def test_the_notebook_renders_the_behavior_section():
    rendered = [
        cell
        for cell in ast.parse(SOURCE).body
        if isinstance(cell, ast.FunctionDef)
        and any(ast.unparse(node) == "behavior_report()" for node in cell.body)
    ]
    assert len(rendered) == 1


def test_the_chart_export_takes_the_behavior_chart_from_the_notebook():
    assert 'notebook["behavior_chart"]' in (NOTEBOOK.parent / "export_charts.py").read_text()
