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
    from src.stats import compare, spearman

    namespace = {
        "alt": alt,
        "pl": pl,
        "V2_FLAGS": V2_FLAG_NAMES,
        "compare": compare,
        "spearman": spearman,
    }
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
    "API_LEAD",
    "API_OUTCOME_TITLES",
    "api_title",
    "DOT_STROKE",
    "IQR_OPACITY",
    "IQR_WIDTH",
    "SURFACE",
    "V2_LEADS",
    "V2_SCOPES",
    "V2_MEASURES",
    "SPEARMAN_CELL_PX",
    "DIVERGING",
    "n_label_expr",
    "iqr_bar",
    "v2_cells",
    "by_cell",
    "v2_measures",
    "v2_summary",
    "v2_failures",
    "flag_comparison",
    "varied_measures",
    "spearman_table",
    "spearman_matrix",
    "spearman_chart",
)


def v2_row(
    run_id,
    source,
    flags,
    agreement,
    note=None,
    *,
    api=None,
    tokens=1000,
    loc=500,
    exit_code=0,
    reason=None,
):
    return {
        "run_id": run_id,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        **dict(zip(V2_FLAG_NAMES, flags)),
        "exit_code": exit_code,
        "terminal_reason": reason,
        "total_tokens": tokens,
        "api_calls": 10,
        "duration_ms": 60_000,
        "file_count": 5,
        "loc": loc,
        "behavior_agreement_pct": agreement,
        "reference_accept_port_crash": 0,
        "behavior_note": note,
        "api_agreement_pct": api,
    }


V2_RUNS = [
    v2_row("a", "python", (0, 1, 1), 99.0, api=90.0, tokens=1000, loc=400),
    v2_row("b", "python", (0, 1, 1), 97.0, api=95.0, tokens=3000, loc=600),
    v2_row("c", "python", (1, 1, 1), 96.0, api=80.0, tokens=2000, loc=700),
    v2_row(
        "d", "javascript", (0, 0, 0), 0.0, "every pair crashed: no src/index.ts", api=0.0, tokens=4000, loc=900
    ),
]
# Every finished attempt: the exit-0 runs above plus the ones the forward tables exclude.
V2_ATTEMPTS = [
    *V2_RUNS,
    v2_row("killed", "python", (0, 1, 1), None, tokens=500, exit_code=137),
    v2_row("failed", "javascript", (0, 0, 0), None, tokens=None, exit_code=1, reason="api_error"),
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
    assert marks == ["rule", "tick", "point"]
    assert panels[0]["layer"][1]["encoding"]["y"]["field"] == "value"
    assert panels[0]["layer"][1]["encoding"]["y"]["aggregate"] == "median"
    x = panels[0]["layer"][2]["encoding"]["x"]
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


def test_the_behavior_chart_draws_the_interquartile_range_behind_the_dots():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    spec = namespace["behavior_chart"](pl.DataFrame(V2_RUNS)).to_dict()
    iqr = spec["concat"][0]["layer"][0]
    assert iqr["mark"]["type"] == "rule"
    assert iqr["mark"]["color"] == namespace["DOT_STROKE"]
    assert iqr["mark"]["opacity"] < 0.5
    assert iqr["encoding"]["y"]["aggregate"] == "q1"
    assert iqr["encoding"]["y2"]["aggregate"] == "q3"


def test_every_behavior_panel_labels_each_condition_with_its_n():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    for metric in ("behavior_agreement_pct", "reference_accept_port_crash"):
        spec = namespace["behavior_chart"](pl.DataFrame(V2_RUNS), metric).to_dict()
        python, javascript = (panel["layer"][2]["encoding"]["x"]["axis"]["labelExpr"] for panel in spec["concat"])
        assert "'source + target': 'n=2'" in python
        assert "'all': 'n=1'" in python
        assert "'none': 'n=0'" in python
        assert "'none': 'n=1'" in javascript


def summary_row(table, source, condition):
    import polars as pl

    return table.filter(
        (pl.col("source_language") == source) & (pl.col("condition") == condition)
    ).row(0, named=True)


def test_the_v2_summary_has_n_exclusions_and_the_quartiles_of_every_lead():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    table = namespace["v2_summary"](pl.DataFrame(V2_RUNS), pl.DataFrame(V2_ATTEMPTS))
    assert table.height == 16
    row = summary_row(table, "python", "source + target")
    assert row["n"] == 2
    assert row["excluded_exit_137"] == 1
    assert row["excluded_exit_1"] == 0
    assert row["median_behavior_agreement_pct"] == 98.0
    assert row["q1_behavior_agreement_pct"] == 97.5
    assert row["q3_behavior_agreement_pct"] == 98.5
    assert row["median_api_agreement_pct"] == 92.5
    assert (row["q1_total_tokens"], row["median_total_tokens"], row["q3_total_tokens"]) == (
        1500.0,
        2000.0,
        2500.0,
    )
    assert row["median_loc"] == 500.0
    empty = summary_row(table, "python", "none")
    assert (empty["n"], empty["excluded_exit_137"]) == (0, 0)
    assert summary_row(table, "javascript", "none")["excluded_exit_1"] == 1


def test_the_failure_table_counts_exits_and_tokens_per_successful_run():
    import polars as pl

    table = definitions(*CHART_NAMES)["v2_failures"](pl.DataFrame(V2_ATTEMPTS))
    assert table.height == 16
    python = summary_row(table, "python", "source + target")
    assert (python["attempts"], python["exit_0"], python["exit_137"], python["api_error"]) == (
        3,
        2,
        1,
        0,
    )
    # Every token the cell spent, the killed run's included, over its two exit-0 runs.
    assert python["tokens_per_success"] == (1000 + 3000 + 500) / 2
    javascript = summary_row(table, "javascript", "none")
    assert (javascript["exit_0"], javascript["api_error"]) == (1, 1)
    assert javascript["tokens_per_success"] == 4000
    assert summary_row(table, "python", "none")["tokens_per_success"] is None


def test_the_flag_comparison_has_a_row_per_flag_pooled_and_per_source():
    import polars as pl

    table = definitions(*CHART_NAMES)["flag_comparison"](
        pl.DataFrame(V2_RUNS), "behavior_agreement_pct"
    )
    assert table.height == 9
    assert table.columns[:2] == ["flag", "source_language"]
    for column in ("n_on", "n_off", "gap", "p", "low", "high", "minimum_detectable_gap"):
        assert column in table.columns
    pooled = table.filter(
        (pl.col("flag") == "include_unit_tests") & (pl.col("source_language") == "pooled")
    ).row(0, named=True)
    assert (pooled["n_on"], pooled["n_off"]) == (1, 3)
    assert pooled["gap"] == 96.0 - 97.0
    python = table.filter(
        (pl.col("flag") == "include_unit_tests") & (pl.col("source_language") == "python")
    ).row(0, named=True)
    assert (python["n_on"], python["n_off"]) == (1, 2)


def test_the_spearman_table_ranks_every_varied_measure_against_behavior_agreement():
    import polars as pl

    table = definitions(*CHART_NAMES)["spearman_table"](pl.DataFrame(V2_RUNS))
    measures = table["measure"].to_list()
    assert "behavior_agreement_pct" not in measures
    # Constant over these runs, so its rank correlation is undefined.
    assert "reference_accept_port_crash" not in measures
    assert set(measures) == {"api_agreement_pct", "total_tokens", "loc"}
    # agreement 99, 97, 96, 0 against loc 400, 600, 700, 900: a reversed order.
    assert round(table.filter(pl.col("measure") == "loc")["rho"][0], 9) == -1.0
    assert table["rho"].abs().to_list() == sorted(table["rho"].abs().to_list(), reverse=True)


def test_the_spearman_heatmap_is_titled_in_prose_and_draws_every_pair():
    import polars as pl

    spec = definitions(*CHART_NAMES)["spearman_chart"](pl.DataFrame(V2_RUNS)).to_dict()
    assert spec["title"]["text"] == "How per-run measures rank against each other on V2 runs (Spearman)"
    cells = spec["layer"][0]
    assert cells["mark"]["type"] == "rect"
    assert len(spec["datasets"][spec["data"]["name"]]) == 4 * 4


def test_the_spearman_heatmap_diverges_through_grey_without_passing_through_another_hue():
    import polars as pl

    spec = definitions(*CHART_NAMES)["spearman_chart"](pl.DataFrame(V2_RUNS)).to_dict()
    color = spec["layer"][0]["encoding"]["color"]
    assert color["scale"]["domain"] == [-1, 0, 1]
    assert color["scale"]["interpolate"] == "lab"
    assert color["legend"]["format"] == ".1f"


def test_the_v2_statistics_lead_with_held_out_behavior_and_api_agreement():
    leads = definitions(*CHART_NAMES)["V2_LEADS"]
    assert leads[:2] == ["behavior_agreement_pct", "api_agreement_pct"]


def test_v2_runs_carry_api_agreement_for_the_statistics():
    assert "'api_agreement_pct': codebase.api_agreement_pct" in assigned("v2_runs")
    assert "api_agreement_pct" not in assigned("V2_NOT_MEASURED")


def test_the_flag_comparison_reads_api_agreement():
    import polars as pl

    table = definitions(*CHART_NAMES)["flag_comparison"](pl.DataFrame(V2_RUNS), "api_agreement_pct")
    pooled = table.filter(
        (pl.col("flag") == "include_unit_tests") & (pl.col("source_language") == "pooled")
    ).row(0, named=True)
    assert pooled["gap"] == 80.0 - 90.0


def test_v2_runs_carry_their_size():
    from types import SimpleNamespace

    size_columns = definitions("size_columns")["size_columns"]
    assert size_columns(SimpleNamespace(file_count=5, loc=500)) == {"file_count": 5, "loc": 500}


def test_the_v2_attempts_keep_runs_that_exited_nonzero():
    assert "include_nonzero_exit=True" in assigned("v2_attempts")


def test_how_to_read_describes_the_v2_study_and_marks_the_v1_sections():
    (cell,) = [
        cell
        for cell in ast.parse(SOURCE).body
        if isinstance(cell, ast.FunctionDef) and "## Statistical analysis" in ast.unparse(cell)
    ]
    text = ast.unparse(cell)
    assert "16 cells" in text
    assert "12 runs" in text
    assert "V1" in text


def test_the_notebook_renders_the_v2_statistics_section():
    rendered = [
        cell
        for cell in ast.parse(SOURCE).body
        if isinstance(cell, ast.FunctionDef)
        and any(ast.unparse(node) == "v2_statistics_report()" for node in cell.body)
    ]
    assert len(rendered) == 1


def test_the_chart_export_takes_the_spearman_heatmap_from_the_notebook():
    assert 'notebook["spearman_chart"]' in (NOTEBOOK.parent / "export_charts.py").read_text()


def test_the_api_section_measures_v2_runs_only():
    assert "for codebase in v2_codebases" in assigned("v2_api_runs")


API_STATUSES = ("ok", "error", "crash")
API_OUTCOMES = {"match": 1, "mismatch": 0, "error_match": 0, "error_mismatch": 0, "crash": 0}
API_CONFUSION = {reference: dict.fromkeys(API_STATUSES, 0) for reference in API_STATUSES}
API_NAMES = (*CHART_NAMES, "api_chart", "api_runs")


def api_row(run_id, source, flags, agreement, note=None):
    return {
        "run_id": run_id,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        **dict(zip(V2_FLAG_NAMES, flags)),
        "api_agreement_pct": agreement,
        "api_crash": 0,
        "api_reference_ok_port_crash": 0,
        "api_note": note,
    }


API_RUNS = [
    api_row("a", "python", (0, 1, 1), 99.0),
    api_row("b", "python", (0, 1, 1), 97.0),
    api_row("c", "python", (1, 1, 1), 96.0),
    api_row("d", "javascript", (0, 0, 0), 0.0, "every case crashed: no src/index.ts"),
]


def test_a_v2_run_carries_api_agreement_every_outcome_and_status_count_and_a_note():
    from types import SimpleNamespace

    api_columns = definitions("api_columns")["api_columns"]
    codebase = SimpleNamespace(
        api_agreement_pct=100.0, api_outcomes=API_OUTCOMES, api_confusion=API_CONFUSION, api_note=None
    )
    columns = api_columns(codebase)
    assert columns["api_agreement_pct"] == 100.0
    assert columns["api_note"] is None
    assert [column for column in columns if column in {f"api_{o}" for o in API_OUTCOMES}] == [
        "api_match",
        "api_mismatch",
        "api_error_match",
        "api_error_mismatch",
        "api_crash",
    ]
    assert len([column for column in columns if column.startswith("api_reference_")]) == 9
    assert "api_reference_ok_port_crash" in columns


def test_the_api_chart_draws_a_dot_per_run_and_a_median_tick_per_condition_on_0_to_100():
    import polars as pl

    namespace = definitions(*API_NAMES)
    spec = namespace["api_chart"](pl.DataFrame(API_RUNS)).to_dict()
    assert spec["title"]["text"] == "Held-out API agreement with the reference (%)"
    panels = spec["concat"]
    assert [panel["title"]["text"] for panel in panels] == [
        "python → javascript",
        "javascript → python",
    ]
    marks = [layer["mark"]["type"] for layer in panels[0]["layer"]]
    assert marks == ["rule", "tick", "point"]
    assert panels[0]["layer"][1]["encoding"]["y"]["aggregate"] == "median"
    assert panels[0]["layer"][2]["encoding"]["y"]["scale"]["domain"] == [0, 100]
    x = panels[0]["layer"][2]["encoding"]["x"]
    assert x["scale"]["domain"] == [label for label, *_ in namespace["V2_CONDITIONS"]]
    datasets = spec["datasets"]
    assert len(datasets[panels[0]["data"]["name"]]) == 3
    assert len(datasets[panels[1]["data"]["name"]]) == 1


def test_the_api_chart_draws_the_interquartile_range_and_labels_each_condition_with_its_n():
    import polars as pl

    namespace = definitions(*API_NAMES)
    spec = namespace["api_chart"](pl.DataFrame(API_RUNS)).to_dict()
    iqr = spec["concat"][0]["layer"][0]
    assert iqr["encoding"]["y"]["aggregate"] == "q1"
    assert iqr["encoding"]["y2"]["aggregate"] == "q3"
    python = spec["concat"][0]["layer"][2]["encoding"]["x"]["axis"]["labelExpr"]
    assert "'source + target': 'n=2'" in python


def test_the_api_chart_titles_an_outcome_and_a_status_count_in_prose():
    import polars as pl

    api_chart = definitions(*API_NAMES)["api_chart"]
    frame = pl.DataFrame(API_RUNS)
    titles = [
        api_chart(frame, column).to_dict()["title"]["text"]
        for column in ("api_crash", "api_reference_ok_port_crash")
    ]
    assert titles == [
        "Cases where either side crashed",
        "Cases the reference runs without raising and the port crashes on",
    ]


def test_every_api_column_has_a_prose_title():
    api_title = definitions(*API_NAMES)["api_title"]
    outcomes = [f"api_{outcome}" for outcome in API_OUTCOMES]
    statuses = [f"api_reference_{a}_port_{b}" for a in API_STATUSES for b in API_STATUSES]
    titles = [api_title(column) for column in outcomes + statuses]
    assert len(set(titles)) == 14
    assert not any("_" in title for title in titles)


def test_the_api_run_table_shows_the_note_of_a_port_that_never_loaded():
    import polars as pl

    runs = definitions(*API_NAMES)["api_runs"](pl.DataFrame(API_RUNS))
    row = runs.filter(pl.col("run_id") == "d").row(0, named=True)
    assert row["condition"] == "none"
    assert row["api_agreement_pct"] == 0.0
    assert row["api_note"] == "every case crashed: no src/index.ts"


def rendered_cell(call: str) -> int:
    cells = [
        index
        for index, cell in enumerate(ast.parse(SOURCE).body)
        if isinstance(cell, ast.FunctionDef)
        and any(ast.unparse(node) == call for node in cell.body)
    ]
    assert len(cells) == 1
    return cells[0]


def test_the_notebook_renders_the_api_section_right_after_the_behavior_section():
    # The API section's heading cell sits between the two reports.
    assert rendered_cell("api_report()") == rendered_cell("behavior_report()") + 2


def test_the_chart_export_takes_the_api_chart_from_the_notebook():
    assert 'notebook["api_chart"]' in (NOTEBOOK.parent / "export_charts.py").read_text()
