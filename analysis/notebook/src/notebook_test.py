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
    "AST_LEADS",
    "AST_TITLES",
    "ast_title",
    "TRANSCRIPT_LEADS",
    "TRANSCRIPT_TITLES",
    "transcript_title",
    "metric_title",
    "METRIC_TITLES",
    "lead_title",
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
    "SPEARMAN_READING",
    "spearman_table",
    "DRIVER_STATUSES",
    "behavior_driver_status",
    "api_driver_status",
    "driver_status_counts",
    "driven_title",
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
    suites=0,
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
        "ast_matched_fraction": None,
        "ast_tree_edit_median": None,
        "ast_branching_wasserstein": None,
        "ast_mean_edge_recall": None,
        "ast_median_trace_normalised": None,
        "read_source_tests": 0,
        "read_target_tests": 0,
        "suite_run_count": suites,
        "own_tests_written": 0,
        "files_read_before_first_write": 6,
        "reread_count": 2,
    }


V2_RUNS = [
    v2_row("a", "python", (0, 1, 1), 99.0, api=90.0, tokens=1000, loc=400, suites=3),
    v2_row("b", "python", (0, 1, 1), 97.0, api=95.0, tokens=3000, loc=600, suites=5),
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
    assert row["median_suite_run_count"] == 4.0
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

    table = definitions(*CHART_NAMES)["spearman_table"](pl.DataFrame(V2_RUNS)).filter(
        pl.col("source_language") == "pooled"
    )
    measures = table["measure"].to_list()
    assert "behavior_agreement_pct" not in measures
    # Constant over these runs, so its rank correlation is undefined.
    assert "reference_accept_port_crash" not in measures
    assert set(measures) == {"api_agreement_pct", "total_tokens", "loc", "suite_run_count"}
    # agreement 99, 97, 96, 0 against loc 400, 600, 700, 900: a reversed order.
    assert round(table.filter(pl.col("measure") == "loc")["rho"][0], 9) == -1.0
    assert table["rho"].abs().to_list() == sorted(table["rho"].abs().to_list(), reverse=True)


def test_the_spearman_table_also_ranks_within_each_source_language():
    import polars as pl

    table = definitions(*CHART_NAMES)["spearman_table"](pl.DataFrame(V2_RUNS))
    # One javascript run: nothing varies within it, so it has no rows.
    assert table["source_language"].unique(maintain_order=True).to_list() == ["pooled", "python"]
    python = table.filter(pl.col("source_language") == "python")
    # Within python, agreement 99, 97, 96 against loc 400, 600, 700.
    assert round(python.filter(pl.col("measure") == "loc")["rho"][0], 9) == -1.0
    assert set(python["n"].to_list()) == {3}
    assert python["rho"].abs().to_list() == sorted(python["rho"].abs().to_list(), reverse=True)


def test_the_spearman_reading_names_the_pooling_and_the_lead_components():
    reading = definitions("SPEARMAN_READING")["SPEARMAN_READING"]
    assert "each source language" in reading
    assert "by definition" in reading


def test_the_spearman_heatmap_is_titled_in_prose_and_draws_every_pair():
    import polars as pl

    spec = definitions(*CHART_NAMES)["spearman_chart"](pl.DataFrame(V2_RUNS)).to_dict()
    assert spec["title"]["text"] == "How per-run measures rank against each other on V2 runs (Spearman)"
    cells = spec["layer"][0]
    assert cells["mark"]["type"] == "rect"
    assert len(spec["datasets"][spec["data"]["name"]]) == 5 * 5


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


def test_the_multiplicity_note_counts_the_tests_and_the_ones_expected_below_005_by_chance():
    note = definitions("multiplicity_note")["multiplicity_note"](135)
    assert "135" in note
    assert "about 7" in note
    assert "exploratory" in note


def test_the_v2_statistics_count_every_flag_comparison_with_a_p():
    (report,) = [
        node
        for node in ast.walk(ast.parse(SOURCE))
        if isinstance(node, ast.FunctionDef) and node.name == "v2_statistics_report"
    ]
    assert "multiplicity_note(" in ast.unparse(report)


def test_the_flag_reading_calls_the_detectable_gap_a_critical_value_detected_about_half_the_time():
    reading = definitions("FLAG_READING")["FLAG_READING"]
    assert "critical value" in reading
    assert "about half" in reading


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


AST_LEAD_NAMES = [
    "ast_matched_fraction",
    "ast_tree_edit_median",
    "ast_branching_wasserstein",
    "ast_mean_edge_recall",
    "ast_median_trace_normalised",
]
AST_NAMES = (*CHART_NAMES, "ast_chart", "ast_runs", "ast_explainers")
ONE_TREE_FIELDS = (
    "node_count",
    "max_depth",
    "function_count",
    "mean_function_lines",
    "max_function_lines",
    "mean_cyclomatic",
    "max_cyclomatic",
)
AST_REPORT = {
    "language": "typescript",
    "port": "/run/ported_implementation",
    "reference": "/reference/packages/gbnf/javascript",
    # compare also reports parsed_file_count, which is not one of the seven delta columns.
    "delta": {
        "parsed_file_count": {"delta": 4, "port": 12, "reference": 8},
        **{
            field: {"delta": index - 3, "port": index, "reference": 3}
            for index, field in enumerate(ONE_TREE_FIELDS)
        },
    },
    "functions": {
        "matched_count": 30,
        "port_only_count": 12,
        "reference_only_count": 10,
        "matched": [],
        "port_only": [],
        "reference_only": [],
        "matched_fraction": 0.75,
        "median_line_drift": -2.5,
    },
    "tree_edit_distance": {"mean_normalised": 0.41, "median_normalised": 0.38},
    "branching": {"port": [1, 1, 2], "reference": [1, 3], "wasserstein": 0.6},
    "api_surface": {
        "shared": ["GBNF/2", "RuleChar"],
        "port_only": ["parse/1"],
        "reference_only": ["RuleRef", "RuleEnd", "default"],
    },
    "call_paths": {
        "entry_point_count": 2,
        "mean_edge_recall": 0.5,
        "median_trace_normalised": 0.25,
        "reachable_fraction_reference": 0.9,
        "reachable_fraction_port": 0.8,
        "unreachable_port_only": ["leftover/0", "spare/1", "unused/2"],
        "entry_points": [],
        "explainer": [
            "GBNF: reference trace of 2 (GBNF, parse); port 2, missing none, extra none",
            "RuleChar: reference trace of 1 (RuleChar); port 0, missing none, extra none",
        ],
    },
}
AST_COLUMNS = [
    *AST_LEAD_NAMES,
    "ast_matched_count",
    "ast_port_only_count",
    "ast_reference_only_count",
    "ast_median_line_drift",
    "ast_tree_edit_mean",
    "ast_api_shared",
    "ast_api_port_only",
    "ast_api_reference_only",
    "ast_entry_point_count",
    "ast_reachable_fraction_reference",
    "ast_reachable_fraction_port",
    "ast_unreachable_port_only",
    *(f"ast_delta_{field}" for field in ONE_TREE_FIELDS),
]


def with_ast(runs, matched, tree_edit, wasserstein, note=None):
    return [
        {
            **run,
            "ast_matched_fraction": m,
            "ast_tree_edit_median": t,
            "ast_branching_wasserstein": w,
            "ast_mean_edge_recall": m,
            "ast_median_trace_normalised": t,
            "ast_matched_count": None if m is None else round(40 * m),
            "ast_note": note if m is None else None,
        }
        for run, m, t, w in zip(runs, matched, tree_edit, wasserstein)
    ]


AST_RUNS = with_ast(
    V2_RUNS,
    [0.8, 0.7, 0.6, None],
    [0.2, 0.3, 0.4, None],
    [0.5, 0.25, 1.0, None],
    "no typescript file parsed under /run/ported_implementation",
)


def test_a_v2_run_carries_every_ast_column_from_the_compare_report():
    from types import SimpleNamespace

    ast_columns = definitions("AST_TITLES", "ast_columns")["ast_columns"]
    columns = ast_columns(SimpleNamespace(ast_report=AST_REPORT, ast_note=None))
    assert list(columns) == [*AST_COLUMNS, "ast_note"]
    assert [columns[lead] for lead in AST_LEAD_NAMES] == [0.75, 0.38, 0.6, 0.5, 0.25]
    assert (
        columns["ast_matched_count"],
        columns["ast_port_only_count"],
        columns["ast_reference_only_count"],
    ) == (30, 12, 10)
    assert (columns["ast_median_line_drift"], columns["ast_tree_edit_mean"]) == (-2.5, 0.41)
    assert (
        columns["ast_api_shared"],
        columns["ast_api_port_only"],
        columns["ast_api_reference_only"],
    ) == (2, 1, 3)
    assert [columns[f"ast_delta_{field}"] for field in ONE_TREE_FIELDS] == [-3, -2, -1, 0, 1, 2, 3]
    assert (
        columns["ast_entry_point_count"],
        columns["ast_reachable_fraction_reference"],
        columns["ast_reachable_fraction_port"],
        columns["ast_unreachable_port_only"],
    ) == (2, 0.9, 0.8, 3)
    assert columns["ast_note"] is None


def test_a_port_compare_could_not_measure_has_null_ast_columns_and_the_error_as_its_note():
    from types import SimpleNamespace

    ast_columns = definitions("AST_TITLES", "ast_columns")["ast_columns"]
    note = "no typescript file parsed under /run/ported_implementation"
    columns = ast_columns(SimpleNamespace(ast_report=None, ast_note=note))
    assert list(columns) == [*AST_COLUMNS, "ast_note"]
    assert [columns[column] for column in AST_COLUMNS] == [None] * len(AST_COLUMNS)
    assert columns["ast_note"] == note


def test_v2_runs_carry_the_ast_columns():
    assert "**ast_columns(codebase)" in assigned("v2_runs")


def test_v2_runs_read_median_line_drift_as_a_float_whether_compare_wrote_an_int_or_a_float():
    assert "'ast_median_line_drift': pl.Float64" in assigned("v2_runs")


def test_the_v2_statistics_compare_flags_on_the_five_ast_leads():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    assert namespace["V2_LEADS"][2:7] == AST_LEAD_NAMES
    assert set(AST_LEAD_NAMES) <= set(namespace["v2_measures"](pl.DataFrame(AST_RUNS)))
    table = namespace["flag_comparison"](pl.DataFrame(AST_RUNS), "ast_matched_fraction")
    pooled = table.filter(
        (pl.col("flag") == "include_unit_tests") & (pl.col("source_language") == "pooled")
    ).row(0, named=True)
    assert (pooled["n_on"], pooled["n_off"]) == (1, 2)
    assert round(pooled["gap"], 9) == round(0.6 - 0.75, 9)


def test_the_spearman_table_ranks_the_ast_leads_against_behavior_agreement():
    import polars as pl

    table = definitions(*CHART_NAMES)["spearman_table"](pl.DataFrame(AST_RUNS)).filter(
        pl.col("source_language") == "pooled"
    )
    assert set(AST_LEAD_NAMES) <= set(table["measure"].to_list())
    # Three runs carry both: the failed port has no AST measure.
    assert table.filter(pl.col("measure") == "ast_matched_fraction")["n"][0] == 3


def test_the_ast_leads_are_titled_in_prose():
    ast_title = definitions(*CHART_NAMES)["ast_title"]
    assert [ast_title(lead) for lead in AST_LEAD_NAMES] == [
        "Share of the reference's functions the port has a counterpart for",
        "Median tree edit distance between paired functions, normalised",
        "Distance between the port's and the reference's branching distributions",
        "Share of the reference's call edges the port also makes, mean over entry points",
        "Edit distance between the reference's and the port's call traces, median over entry points",
    ]


def test_every_ast_column_has_a_prose_title():
    titles = definitions(*CHART_NAMES)["AST_TITLES"]
    assert list(titles) == AST_COLUMNS
    assert len(set(titles.values())) == len(AST_COLUMNS)
    assert not any("_" in title for title in titles.values())


def test_the_ast_chart_draws_dots_a_median_tick_and_the_interquartile_range_per_condition():
    import polars as pl

    namespace = definitions(*AST_NAMES)
    spec = namespace["ast_chart"](pl.DataFrame(AST_RUNS), "ast_tree_edit_median").to_dict()
    assert spec["title"]["text"] == "Median tree edit distance between paired functions, normalised"
    panels = spec["concat"]
    assert [panel["title"]["text"] for panel in panels] == [
        "python → javascript",
        "javascript → python",
    ]
    iqr, median, points = panels[0]["layer"]
    assert [layer["mark"]["type"] for layer in (iqr, median, points)] == ["rule", "tick", "point"]
    assert (iqr["encoding"]["y"]["aggregate"], iqr["encoding"]["y2"]["aggregate"]) == ("q1", "q3")
    assert median["encoding"]["y"]["aggregate"] == "median"
    assert points["encoding"]["x"]["scale"]["domain"] == [
        label for label, *_ in namespace["V2_CONDITIONS"]
    ]
    assert "'source + target': 'n=2'" in points["encoding"]["x"]["axis"]["labelExpr"]
    # Not a percentage: the axis starts at zero instead of spanning 0 to 100.
    assert points["encoding"]["y"]["scale"] == {"zero": True}


def test_the_ast_chart_leads_with_the_matched_fraction():
    import polars as pl

    spec = definitions(*AST_NAMES)["ast_chart"](pl.DataFrame(AST_RUNS)).to_dict()
    assert spec["title"]["text"] == "Share of the reference's functions the port has a counterpart for"


def test_the_ast_run_table_shows_the_note_of_a_port_compare_could_not_measure():
    import polars as pl

    runs = definitions(*AST_NAMES)["ast_runs"](pl.DataFrame(AST_RUNS))
    assert runs.columns[:8] == ["run_id", "source_language", "condition", *AST_LEAD_NAMES]
    assert runs.columns[-1] == "ast_note"
    row = runs.filter(pl.col("run_id") == "d").row(0, named=True)
    assert row["condition"] == "none"
    assert row["ast_matched_fraction"] is None
    assert row["ast_note"] == "no typescript file parsed under /run/ported_implementation"


def test_v2_ast_explainers_hold_one_row_per_compare_explainer_sentence():
    assert "codebase.ast_report['call_paths']['explainer']" in assigned("v2_ast_explainers")


def test_the_ast_explainer_table_groups_each_runs_sentences_under_its_condition():
    import polars as pl

    explainers = pl.DataFrame(
        {
            "run_id": ["b", "a", "a"],
            "explainer": ["b: one", "a: one", "a: two"],
        }
    )
    tables = definitions(*AST_NAMES)["ast_explainers"](pl.DataFrame(AST_RUNS), explainers)
    assert {label: table["explainer"].to_list() for label, table in tables.items()} == {
        "a · python · source + target": ["a: one", "a: two"],
        "b · python · source + target": ["b: one"],
    }
    assert list(tables) == ["a · python · source + target", "b · python · source + target"]


def test_the_notebook_renders_the_ast_section_right_after_the_api_section():
    assert rendered_cell("ast_report()") == rendered_cell("api_report()") + 2


def test_the_chart_export_takes_the_ast_chart_from_the_notebook():
    assert 'notebook["ast_chart"]' in (NOTEBOOK.parent / "export_charts.py").read_text()
TRANSCRIPT_LEAD_NAMES = [
    "read_source_tests",
    "read_target_tests",
    "suite_run_count",
    "own_tests_written",
    "files_read_before_first_write",
    "reread_count",
]
TRANSCRIPT_REPORT = {
    "turns": 21,
    "bash_calls": 21,
    "read_calls": 0,
    "write_calls": 0,
    "edit_calls": 0,
    "search_calls": 0,
    "read_source": 4,
    "read_source_tests": 2,
    "read_target_tests": 9,
    "touched_source_tests": True,
    "touched_target_tests": True,
    "suite_runs": [{"turn": 18, "command": "pytest", "suite": "unknown", "passed": 320, "failed": 0}],
    "suite_run_count": 2,
    "last_suite_counts": {"target_tests": {"passed": 320, "failed": 1}},
    "own_tests_written": 1,
    "own_test_files": ["/target/tests/conftest.py"],
    "differential_script": True,
    "differential_evidence": {"turn": 16, "command": "python3 a.py && node b.js"},
    "fetch_attempts": 0,
    "fetch_commands": [],
    "input_tokens": 42,
    "output_tokens": 30559,
    "cache_read_tokens": 1176607,
    "cache_creation_tokens": 73505,
    "tokens_before_first_write": 443246,
    "tokens_after_first_write": 837467,
    "first_write_turn": 11,
    "last_suite_run_turn": 18,
    "first_read_path": "/input/python/README.md",
    "first_read_class": "source",
    "first_read_is_entry_point": True,
    "files_read_before_first_write": 7,
    "source_files_read_before_first_write": 3,
    "reread_count": 4,
    "max_rereads_of_one_file": 2,
    "max_rereads_path": "/input/python/gbnf/graph.py",
    "search_calls_per_file_read": 0.5,
    "read_order": ["/input/python/README.md", "/input/python/gbnf/__init__.py"],
    "reads_after_last_write": 1,
}
TRANSCRIPT_NAMES = (
    *CHART_NAMES,
    "TRANSCRIPT_COUNTED",
    "transcript_chart",
    "transcript_counts",
    "transcript_runs",
    "TRANSCRIPT_FIRST_READ",
    "TRANSCRIPT_QUOTED",
    "FIRST_READ_CLASSES",
    "first_read_counts",
)


def transcript_columns(report=TRANSCRIPT_REPORT):
    from types import SimpleNamespace

    namespace = definitions("transcript_columns", "TRANSCRIPT_DROPPED", "SUITE_CLASSES")
    return namespace["transcript_columns"](SimpleNamespace(transcript=report))


def transcript_row(
    run_id, source, flags, *, suites, touched=False, differential=False, first_write=11, entry=True, first_class="source"
):
    return {
        "run_id": run_id,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        **dict(zip(V2_FLAG_NAMES, flags)),
        **transcript_columns(),
        "suite_run_count": suites,
        "touched_target_tests": touched,
        "differential_script": differential,
        "first_write_turn": first_write,
        "first_read_is_entry_point": entry,
        "first_read_class": first_class,
    }


def transcript_frame():
    import polars as pl

    return pl.DataFrame(
        [
            transcript_row("a", "python", (0, 1, 1), suites=3, touched=True, differential=True),
            transcript_row("b", "python", (0, 1, 1), suites=5, touched=True, entry=None, first_class="other"),
            transcript_row("c", "python", (1, 1, 1), suites=0, first_write=None, entry=False),
            transcript_row("d", "javascript", (0, 0, 0), suites=1),
        ]
    )


def test_v2_runs_carry_the_transcript_leads_for_the_statistics():
    assert ast.literal_eval(assigned("TRANSCRIPT_LEADS")) == TRANSCRIPT_LEAD_NAMES
    assert "codebase.transcript[lead] for lead in TRANSCRIPT_LEADS" in assigned("v2_runs")


def test_the_transcript_section_measures_v2_runs_only():
    assert "for codebase in v2_codebases" in assigned("v2_transcript_runs")


def test_a_v2_run_carries_every_transcript_count_but_the_cache_split_of_its_tokens():
    columns = transcript_columns()
    for dropped in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens"):
        assert dropped not in columns
    assert (columns["tokens_before_first_write"], columns["tokens_after_first_write"]) == (443246, 837467)
    assert [column for column in TRANSCRIPT_LEAD_NAMES if column not in columns] == []
    assert (columns["touched_target_tests"], columns["differential_script"]) == (True, True)


def test_a_v2_run_carries_the_last_pass_and_fail_counts_of_each_suite_class():
    columns = transcript_columns()
    assert (columns["last_target_tests_passed"], columns["last_target_tests_failed"]) == (320, 1)
    assert columns["last_own_tests_passed"] is None
    assert len([column for column in columns if column.startswith("last_") and column != "last_suite_run_turn"]) == 8


def test_a_v2_run_quotes_the_differential_evidence_and_holds_no_lists():
    columns = transcript_columns()
    assert columns["differential_evidence"] == "python3 a.py && node b.js"
    written = transcript_columns({**TRANSCRIPT_REPORT, "differential_evidence": {"turn": 4, "path": "/target/diff.py"}})
    assert written["differential_evidence"] == "/target/diff.py"
    absent = transcript_columns({**TRANSCRIPT_REPORT, "differential_evidence": None})
    assert absent["differential_evidence"] is None
    assert not any(isinstance(value, (list, dict)) for value in columns.values())


def test_every_charted_transcript_column_has_a_prose_title():
    namespace = definitions(*TRANSCRIPT_NAMES)
    charted = [
        column
        for column in transcript_columns()
        if column not in (*namespace["TRANSCRIPT_COUNTED"], *namespace["TRANSCRIPT_FIRST_READ"], *namespace["TRANSCRIPT_QUOTED"])
    ]
    titles = [namespace["transcript_title"](column) for column in charted]
    assert len(set(titles)) == len(charted)
    assert not any("_" in title for title in titles)
    assert set(namespace["TRANSCRIPT_TITLES"]) == set(charted)


def test_the_transcript_chart_draws_a_dot_per_run_a_median_tick_and_an_interquartile_bar_from_zero():
    import polars as pl

    namespace = definitions(*TRANSCRIPT_NAMES)
    spec = namespace["transcript_chart"](transcript_frame(), "suite_run_count").to_dict()
    assert spec["title"]["text"] == "Test suite runs"
    panels = spec["concat"]
    assert [panel["title"]["text"] for panel in panels] == ["python → javascript", "javascript → python"]
    layers = panels[0]["layer"]
    assert [layer["mark"]["type"] for layer in layers] == ["rule", "tick", "point"]
    assert layers[0]["encoding"]["y"]["aggregate"] == "q1"
    assert layers[1]["encoding"]["y"]["aggregate"] == "median"
    assert layers[2]["encoding"]["y"]["scale"] == {"zero": True}
    assert "'source + target': 'n=2'" in layers[2]["encoding"]["x"]["axis"]["labelExpr"]


def test_the_transcript_chart_leaves_a_run_without_a_value_out_of_the_dots_and_the_n():
    import polars as pl

    namespace = definitions(*TRANSCRIPT_NAMES)
    spec = namespace["transcript_chart"](transcript_frame(), "first_write_turn").to_dict()
    python = spec["concat"][0]
    assert len(spec["datasets"][python["data"]["name"]]) == 2
    assert "'all': 'n=0'" in python["layer"][2]["encoding"]["x"]["axis"]["labelExpr"]


def test_the_transcript_table_counts_runs_that_touched_the_target_tests_or_ran_a_differential_script():
    import polars as pl

    table = definitions(*TRANSCRIPT_NAMES)["transcript_counts"](transcript_frame())
    assert table.height == 16
    row = summary_row(table, "python", "source + target")
    assert (row["n"], row["touched_target_tests"], row["differential_script"]) == (2, 2, 1)
    empty = summary_row(table, "python", "none")
    assert (empty["n"], empty["touched_target_tests"], empty["differential_script"]) == (0, 0, 0)


def test_a_v2_run_quotes_the_source_read_order_as_one_string():
    assert transcript_columns()["read_order"] == "/input/python/README.md → /input/python/gbnf/__init__.py"
    assert transcript_columns({**TRANSCRIPT_REPORT, "read_order": []})["read_order"] == ""


def test_the_first_read_table_counts_entry_point_starts_and_first_read_classes_by_condition():
    import polars as pl

    table = definitions(*TRANSCRIPT_NAMES)["first_read_counts"](transcript_frame())
    assert table.height == 16
    row = summary_row(table, "python", "source + target")
    assert (row["n"], row["entry_point"], row["not_entry_point"], row["no_code_file_read"]) == (2, 1, 0, 1)
    assert (row["first_read_source"], row["first_read_other"], row["first_read_port"]) == (1, 1, 0)
    empty = summary_row(table, "python", "none")
    assert (empty["n"], empty["entry_point"], empty["first_read_source"]) == (0, 0, 0)


def test_the_transcript_run_table_quotes_the_differential_evidence():
    import polars as pl

    runs = definitions(*TRANSCRIPT_NAMES)["transcript_runs"](transcript_frame())
    row = runs.filter(pl.col("run_id") == "a").row(0, named=True)
    assert row["condition"] == "source + target"
    assert row["differential_evidence"] == "python3 a.py && node b.js"
    assert runs.columns[:9] == ["run_id", "source_language", "condition", *TRANSCRIPT_LEAD_NAMES]
    assert row["read_order"] == "/input/python/README.md → /input/python/gbnf/__init__.py"
    assert row["max_rereads_path"] == "/input/python/gbnf/graph.py"


def test_the_per_flag_comparison_and_the_rank_correlations_take_the_transcript_leads():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    assert namespace["V2_LEADS"][-6:] == TRANSCRIPT_LEAD_NAMES
    assert set(TRANSCRIPT_LEAD_NAMES) <= set(namespace["v2_measures"](pl.DataFrame(V2_RUNS)))
    assert namespace["lead_title"]("own_tests_written") == "Test files the agent wrote itself"


def test_the_notebook_renders_the_transcript_section_between_the_ast_section_and_the_statistics():
    assert rendered_cell("transcript_report()") == rendered_cell("ast_report()") + 2
    assert rendered_cell("v2_statistics_report()") == rendered_cell("transcript_report()") + 2


def test_the_chart_export_takes_the_transcript_chart_from_the_notebook():
    assert 'notebook["transcript_chart"]' in (NOTEBOOK.parent / "export_charts.py").read_text()


def confusion_row(run_id, source, flags, agreement, **counts):
    outcomes = ("accept", "reject", "error", "crash")
    return {
        "run_id": run_id,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        **dict(zip(V2_FLAG_NAMES, flags)),
        "behavior_agreement_pct": agreement,
        **{f"reference_{a}_port_{b}": counts.get(f"{a}_{b}", 0) for a in outcomes for b in outcomes},
    }


DRIVER_RUNS = [
    # Every pair crashed: the driver could not load the port.
    confusion_row("gone", "javascript", (1, 0, 0), 0.0, accept_crash=346, reject_crash=376, error_crash=77),
    # Loaded, matches the errors, rejects every input: no accept is reached.
    confusion_row("stuck", "python", (1, 0, 0), 9.6, accept_reject=346, reject_reject=376, error_error=77),
    confusion_row("driven", "python", (1, 0, 0), 97.5, accept_accept=340, accept_reject=6, reject_reject=376, error_error=77),
    confusion_row("unmeasured", "python", (0, 0, 0), None),
]


def test_behavior_driver_status_separates_unloaded_failing_and_driven_ports():
    import polars as pl

    frame = definitions(*CHART_NAMES)["behavior_driver_status"](pl.DataFrame(DRIVER_RUNS))
    assert frame["behavior_driver_status"].to_list() == ["not_loaded", "loaded_failing", "driven", None]


def test_api_driver_status_separates_unloaded_failing_and_driven_ports():
    import polars as pl

    def row(run_id, match, crash, mismatch=0, agreement=1.0):
        return {
            "run_id": run_id,
            "api_agreement_pct": agreement,
            "api_match": match,
            "api_mismatch": mismatch,
            "api_error_match": 5,
            "api_error_mismatch": 0,
            "api_crash": crash,
        }

    frame = pl.DataFrame(
        [
            # Every case crashed: crash counts the cases where either side crashed.
            {**row("gone", 0, 999), "api_error_match": 0},
            row("stuck", 0, 0, 994),
            row("driven", 900, 0, 94),
            {**row("unmeasured", 0, 0), "api_agreement_pct": None},
        ]
    )
    statuses = definitions(*CHART_NAMES)["api_driver_status"](frame)["api_driver_status"].to_list()
    assert statuses == ["not_loaded", "loaded_failing", "driven", None]


def test_driver_status_counts_count_each_status_per_cell():
    import polars as pl

    namespace = definitions(*CHART_NAMES)
    frame = namespace["behavior_driver_status"](pl.DataFrame(DRIVER_RUNS))
    counts = namespace["driver_status_counts"](frame, "behavior_driver_status")
    assert counts.columns == ["source_language", "condition", "n", "not_loaded", "loaded_failing", "driven", "unmeasured"]
    python = counts.filter(pl.col("source_language") == "python").to_dicts()
    assert [(row["n"], row["not_loaded"], row["loaded_failing"], row["driven"], row["unmeasured"]) for row in python] == [(1, 0, 0, 0, 1), (2, 0, 1, 1, 0)]
    javascript = counts.filter(pl.col("source_language") == "javascript").row(0, named=True)
    assert (javascript["n"], javascript["not_loaded"]) == (1, 1)


def test_the_driven_charts_say_so_in_their_titles():
    namespace = definitions(*CHART_NAMES)
    title = namespace["driven_title"](namespace["behavior_title"])
    assert title("behavior_agreement_pct") == "Held-out behavior agreement with the reference (%), driven ports only"


def test_the_behavior_and_api_reports_show_driver_status_and_driven_charts():
    for name in ("behavior_report", "api_report"):
        (report,) = [
            node for node in ast.walk(ast.parse(SOURCE)) if isinstance(node, ast.FunctionDef) and node.name == name
        ]
        text = ast.unparse(report)
        assert "driver_status_counts(" in text
        assert "driven_title(" in text
