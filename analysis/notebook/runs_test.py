import ast
import re
from pathlib import Path

import altair as alt
import polars as pl

from src.Codebase import Codebase
from src.rebuilt_layout import LAYOUT_RULE

NOTEBOOK = Path(__file__).resolve().parent / "runs.py"
SOURCE = NOTEBOOK.read_text()
DIFF_METRICS = [
    "reference_diff_similarity_pct",
    "reference_diff_kept_pct",
    "reference_diff_identical",
    "reference_diff_modified",
    "reference_diff_renamed",
    "reference_diff_added",
    "reference_diff_deleted",
]


def assignment(name: str, source: str = SOURCE) -> ast.expr:
    for node in ast.walk(ast.parse(source)):
        targets = getattr(node, "targets", [])
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return node.value
    raise AssertionError(f"{name} is not assigned in runs.py")


def starred_names(name: str) -> list[str]:
    return [
        element.value.id
        for element in assignment(name).elts
        if isinstance(element, ast.Starred)
    ]


def describe_diff_metrics():
    def it_lists_the_reference_diff_columns():
        assert ast.literal_eval(assignment("DIFF_METRICS")) == DIFF_METRICS

    def it_names_only_properties_of_codebase():
        for metric in ast.literal_eval(assignment("DIFF_METRICS")):
            assert isinstance(getattr(Codebase, metric, None), property)

    def it_registers_a_diff_section():
        keys = [key.value for key in assignment("SECTIONS").keys]
        assert "diff" in keys

    def it_shows_the_diff_in_both_the_forward_and_the_reverse_section():
        assert 'reverse_report("diff")' in SOURCE
        assert 'report("diff")' in SOURCE.replace('reverse_report("diff")', "")

    def it_measures_the_diff_on_forward_and_reverse_runs_alike():
        assert "DIFF_METRICS" in starred_names("METRICS")
        assert "DIFF_METRICS" in starred_names("REVERSE_METRICS")


def function_def(name: str) -> ast.FunctionDef:
    for node in ast.walk(ast.parse(SOURCE)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is not defined in runs.py")


def conditions(source_language: str) -> list[tuple[str, bool, bool]]:
    namespace: dict = {}
    module = ast.Module(body=[function_def("conditions")], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(NOTEBOOK), "exec"), namespace)
    return namespace["conditions"](source_language)


def describe_conditions():
    def it_orders_the_axis_from_no_tests_to_both():
        for source_language in ("python", "typescript"):
            assert [label for label, *_ in conditions(source_language)] == [
                "no tests",
                "source tests",
                "target tests",
                "both tests",
            ]

    def it_calls_the_python_suite_the_source_for_a_python_port():
        assert conditions("python")[1:3] == [
            ("source tests", True, False),
            ("target tests", False, True),
        ]

    def it_calls_the_python_suite_the_target_for_a_typescript_port():
        assert conditions("typescript")[1:3] == [
            ("source tests", False, True),
            ("target tests", True, False),
        ]


COST_COLUMNS = ["total_tokens", "api_calls", "duration"]
SIZE_COLUMNS = ["file_count", "loc", "mean_cyclomatic"]


def describe_cost_section():
    def it_lists_what_the_run_cost():
        assert ast.literal_eval(assignment("COST_COLUMNS")) == COST_COLUMNS

    def it_replaces_the_static_section():
        keys = [key.value for key in assignment("SECTIONS").keys]
        assert "cost" in keys
        assert "static" not in keys


def describe_size_section():
    def it_lists_the_size_columns_apart_from_the_cost_ones():
        assert ast.literal_eval(assignment("SIZE_COLUMNS")) == SIZE_COLUMNS

    def it_registers_a_size_section():
        keys = [key.value for key in assignment("SECTIONS").keys]
        assert "size" in keys

    def it_names_only_size_properties_of_codebase():
        for metric in SIZE_COLUMNS:
            assert isinstance(getattr(Codebase, metric, None), property)

    def it_follows_the_cost_section():
        assert SOURCE.index('report("cost")') < SOURCE.index("### size")
        assert SOURCE.index("### size") < SOURCE.index('report("size")')
        assert SOURCE.index('report("size")') < SOURCE.index("### tests")


TEST_COLUMNS = [
    "adapted_unit_pass_pct",
    "adapted_integration_pass_pct",
    "adapted_integration_coverage_pct",
]


def describe_tests_section():
    def it_lists_the_pass_rates_and_the_coverage():
        assert ast.literal_eval(assignment("TEST_COLUMNS")) == TEST_COLUMNS

    def it_names_only_properties_of_codebase():
        for metric in TEST_COLUMNS:
            assert isinstance(getattr(Codebase, metric, None), property)

    def it_measures_coverage_on_forward_and_reverse_runs_alike():
        metrics = ast.literal_eval(assignment("TEST_METRICS"))
        assert "adapted_integration_coverage_pct" in metrics
        assert "TEST_METRICS" in starred_names("SHARED_METRICS")
        assert "SHARED_METRICS" in starred_names("METRICS")
        assert "SHARED_METRICS" in starred_names("REVERSE_METRICS")

    def it_measures_the_reference_too():
        assert "adapted_integration_coverage_pct" in ast.unparse(function_def("reference_row"))

    def it_leads_the_tests_section_with_the_unit_pass_rate():
        assert assignment("UNIT_LEAD").value == "adapted_unit_pass_pct"
        assert "'Other test columns'" in ast.unparse(assignment("LEAD_COLUMNS"))
        assert "LEAD_COLUMNS" in ast.unparse(function_def("section_chart"))

    def it_keeps_the_unit_columns_in_the_per_run_tables():
        assert "adapted_unit_pass_pct" in ast.literal_eval(assignment("TEST_METRICS"))
        assert "adapt_rules" in ast.literal_eval(assignment("TEST_METRICS"))

    def it_counts_the_shim_rules_per_condition():
        body = ast.unparse(function_def("shim_rules"))
        assert "ports_with_adapt_rules" in body
        assert "adapt_rules" in body
        assert "shim_rules" in ast.unparse(function_def("tests_panel"))


class StubCodebase:
    """Stands in for Codebase so reference_row can be exercised without a real tree."""

    def __init__(self, path, exclude=None, language=None, run_id=None):
        self.run_id = run_id

    file_count = 3
    loc = 100
    mean_cyclomatic = 1.5
    adapted_integration_coverage_pct = 61.5


def reference_row(codebase_class, language="typescript"):
    namespace = {
        "Codebase": codebase_class,
        "EXCLUDE_BY_LANGUAGE": {language: []},
        "REFERENCE": Path("/reference"),
    }
    module = ast.Module(body=[function_def("reference_row")], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(NOTEBOOK), "exec"), namespace)
    return namespace["reference_row"](language)


def describe_reference_row():
    def it_measures_the_reference_under_its_own_run_id():
        assert reference_row(StubCodebase)["adapted_integration_coverage_pct"] == 61.5


def cell_defining(name: str) -> ast.FunctionDef:
    for node in ast.parse(SOURCE).body:
        if isinstance(node, ast.FunctionDef) and any(
            isinstance(target, ast.Name) and target.id == name
            for child in ast.walk(node)
            for target in getattr(child, "targets", [])
        ):
            return node
    raise AssertionError(f"{name} is not assigned in any cell of runs.py")


def calls(name: str) -> list[str]:
    return [
        ast.unparse(node)
        for node in ast.walk(ast.parse(SOURCE))
        if isinstance(node, ast.Call) and ast.unparse(node.func) == name
    ]


def nudges(values: list[float]) -> list[float]:
    namespace: dict = {}
    module = ast.Module(
        body=[
            ast.Assign(
                targets=[ast.Name(id="RATIO_TOLERANCE", ctx=ast.Store())],
                value=assignment("RATIO_TOLERANCE"),
            ),
            function_def("nudges"),
        ],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), str(NOTEBOOK), "exec"), namespace)
    return namespace["nudges"](values)


CHART_BUILDERS = ["chart", "pair_chart", "ratio_chart", "round_trip_chart"]
CHARTED_COLUMNS = [
    "COST_COLUMNS",
    "SIZE_COLUMNS",
    "TEST_COLUMNS",
    "DIFF_METRICS",
    "EMBEDDING_METRICS",
]


def describe_chart_marks():
    def it_draws_no_bar_in_any_chart_builder():
        for builder in CHART_BUILDERS:
            assert "mark_bar" not in ast.unparse(function_def(builder))

    def it_anchors_a_cell_with_a_median_tick_and_never_a_mean():
        for builder in CHART_BUILDERS:
            body = ast.unparse(function_def(builder))
            assert "median_tick" in body
            assert "mean(" not in body

    def it_marks_the_similarity_dots_by_whether_the_port_kept_the_file_layout():
        body = ast.unparse(function_def("chart"))
        assert "if metric == DIFF_LEAD" in body
        assert "shape=layout_shape()" in body
        assert "shape=layout_shape()" in ast.unparse(function_def("round_trip_chart"))

    def it_states_the_layout_rule_in_the_legend():
        assert "LAYOUT_RULE" in ast.unparse(function_def("layout_shape"))
        assert LAYOUT_RULE == "rebuilt: under 10 files kept at their reference path"

    def it_states_the_layout_rule_in_the_how_to_read():
        note = SOURCE[SOURCE.index("### reference diff") :]
        assert "reference_diff_identical + reference_diff_modified < 10" in note

    def it_titles_every_charted_column_in_words():
        titles = ast.literal_eval(assignment("METRIC_TITLES"))
        charted = {
            "duration_min" if column == "duration" else column
            for name in CHARTED_COLUMNS
            for column in ast.literal_eval(assignment(name))
        }
        assert charted <= set(titles)
        assert all("_" not in title for title in titles.values())

    def it_takes_the_panel_title_from_the_words_and_not_the_column():
        assert "title=panel_title(metric_title(metric))" in ast.unparse(function_def("chart"))
        body = ast.unparse(function_def("round_trip_chart"))
        assert "metric_title(DIFF_LEAD)" in body
        assert "f'{DIFF_LEAD}" not in body


def notebook_function(name: str, namespace: dict):
    module = ast.Module(body=[function_def(name)], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(NOTEBOOK), "exec"), namespace)
    return namespace[name]


def fan_out(values: list[float], condition: str = "both tests") -> list[float]:
    rows = pl.DataFrame({"condition": [condition] * len(values), "value": values})
    return notebook_function("fan_out", {"pl": pl})(rows)["nudge"].to_list()


def offset_scale(nudge: list[float], centre: float) -> dict:
    namespace = {
        "alt": alt,
        "DOT_STEP": ast.literal_eval(assignment("DOT_STEP")),
        "BAND_FILL": ast.literal_eval(assignment("BAND_FILL")),
    }
    rows = pl.DataFrame({"nudge": nudge})
    return notebook_function("dot_offset", namespace)(rows, centre).to_dict()["scale"]


def describe_coincident_dots():
    def it_fans_five_runs_at_one_value_out_into_five_dots():
        assert fan_out([100.0] * 5) == [-2.0, -1.0, 0.0, 1.0, 2.0]

    def it_leaves_a_run_with_no_twin_where_it_was():
        assert fan_out([46.5625, 53.125, 100.0]) == [0.0, 0.0, 0.0]

    def it_ranks_each_stack_in_a_stable_order_so_the_export_does_not_churn():
        assert "maintain_order=True" in ast.unparse(function_def("fan_out"))

    def it_measures_the_fan_out_from_the_band_edge_and_not_its_middle():
        assert offset_scale([-2.0, -1.0, 0.0, 1.0, 2.0], 15.0) == {
            "domain": [-2.0, 2.0],
            "range": [3.0, 27.0],
        }

    def it_puts_a_lone_dot_on_the_band_centre():
        scale = offset_scale([0.0], 15.0)
        assert sum(scale["range"]) / 2 == 15.0


def describe_round_trip_chart():
    def it_pairs_a_reverse_leg_with_the_forward_run_it_came_from():
        body = ast.unparse(function_def("round_trip_rows"))
        assert "on='forward_run_id'" in body
        assert "pl.col('run_id').alias('forward_run_id')" in body

    def it_plots_both_legs_of_the_same_similarity_column():
        body = ast.unparse(function_def("round_trip_chart"))
        assert ast.literal_eval(assignment("ROUND_TRIP_LEGS")) == ["forward", "reverse"]
        assert "DIFF_LEAD" in ast.unparse(function_def("round_trip_rows"))
        assert "alt.Scale(domain=[0, 100], nice=False)" in body

    def it_joins_the_two_legs_of_a_run_with_one_line():
        body = ast.unparse(function_def("round_trip_chart"))
        assert "mark_line" in body
        assert "detail=alt.Detail('forward_run_id:N')" in body

    def it_orders_the_x_axis_by_the_forward_condition():
        body = ast.unparse(function_def("round_trip_chart"))
        assert "alt.X('condition:N', sort=[label for label, *_ in conditions(forward_source)]" in body

    def it_folds_the_reverse_only_diff_charts_into_an_accordion():
        body = ast.unparse(function_def("reverse_diff_panel"))
        assert "round_trip_chart(forward_source)" in body
        assert "mo.accordion" in body

    def it_replaces_only_the_reverse_diff_charts():
        body = ast.unparse(function_def("reverse_report"))
        assert "reverse_diff_panel(metrics, by_target, target_language, forward_source) if section == 'diff'" in body

    def it_says_the_reverse_condition_is_constant_in_the_how_to_read():
        note = SOURCE[SOURCE.index("## Reverse ports") :]
        note = note[note.index("### reference diff") :]
        assert "The reverse leg's own condition is constant" in note
        assert "`both tests` cell" in note


def describe_ladder_ratio_chart():
    def it_leaves_a_dot_with_no_neighbour_on_the_centre_line():
        assert nudges([1.0, 2.0, 3.0]) == [0.0, 0.0, 0.0]

    def it_spreads_only_the_dots_that_would_overlap():
        assert nudges([1.0, 1.005, 1.01, 3.0]) == [-1.0, 0.0, 1.0, 0.0]

    def it_puts_the_conditions_on_the_x_axis_in_order():
        body = ast.unparse(function_def("ratio_chart"))
        assert "alt.X('condition:N', sort=[label for label, *_ in conditions(source_language)]" in body

    def it_drops_the_condition_colour():
        assert "condition_colour" not in ast.unparse(function_def("ratio_chart"))

    def it_shares_one_y_domain_across_both_directions():
        assert "ratio_domain()" in ast.unparse(function_def("ratio_chart"))
        domain = ast.unparse(function_def("ratio_domain"))
        assert "runs.select" in domain
        assert "pl.lit(1.0).alias('reference')" in domain

    def it_titles_the_chart_in_words():
        assert "ladder time relative to the reference" in ast.unparse(function_def("ratio_chart"))


def describe_performance_notes():
    def it_takes_no_private_names_out_of_the_codebase_module():
        cell = ast.unparse(cell_defining("performance_notes"))
        assert "_log_log_slope" not in cell
        assert "LADDER_SLOPE_RUNG" not in cell

    def it_reads_the_slope_and_the_reference_rungs_off_the_frame():
        assert ast.literal_eval(assignment("LADDER_NOTE_METRICS")) == [
            "ladder_slope",
            "ladder_reference_slope",
            "ladder_reference_rungs",
        ]
        assert "LADDER_NOTE_METRICS" in starred_names("METRICS")

    def it_names_only_properties_of_codebase():
        for metric in ast.literal_eval(assignment("LADDER_NOTE_METRICS")):
            assert isinstance(getattr(Codebase, metric, None), property)

    def it_keeps_the_slope_out_of_the_summary_tables():
        assert "ladder_slope" not in ast.literal_eval(assignment("PERFORMANCE_METRICS"))

    def it_carries_two_findings_and_an_open_question():
        cell = ast.unparse(cell_defining("performance_notes"))
        for label in ("Scaling", "Failure envelope", "Open question"):
            assert label in cell

    def it_computes_every_number_instead_of_typing_it():
        assert not re.search(r"\d+\.\d+", ast.unparse(cell_defining("performance_notes")))

    def it_reads_both_the_forward_and_the_reverse_frame():
        arguments = {argument.arg for argument in cell_defining("performance_notes").args.args}
        assert {"runs", "reverse_runs"} <= arguments

    def it_renders_the_notes_in_an_accordion():
        stacks = [text for text in calls("mo.vstack") if "performance_notes" in text]
        assert len(stacks) == 1
        assert "### notes" in stacks[0]
        assert "mo.accordion({'Notes':" in stacks[0]

    def it_sits_between_the_ladder_and_the_reverse_ports():
        assert SOURCE.index('report("performance")') < SOURCE.index("performance_notes")
        assert SOURCE.index("performance_notes") < SOURCE.index("## Reverse ports")


def describe_port_to_port_section():
    def it_shows_the_similarity_chart_alone_and_the_rest_in_an_accordion():
        body = ast.unparse(function_def("section_chart"))
        assert "mo.accordion({LEAD_COLUMNS[lead]" in body
        assert "'Other diff columns'" in ast.unparse(assignment("LEAD_COLUMNS"))
        assert assignment("DIFF_LEAD").value == DIFF_METRICS[0]

    def it_pairs_forward_ports_only():
        assert "port_pairs = within_direction_similarity(codebases)" in SOURCE

    def it_summarizes_the_cells_out_of_the_same_pairs_the_dots_draw():
        assert "cell_pairs = within_cell(port_pairs)" in SOURCE
        assert "cell_pairs.filter" in ast.unparse(function_def("pair_summary"))

    def it_scales_the_anchor_axes_over_the_whole_range():
        assert "alt.Scale(domain=[0, 100]" in ast.unparse(function_def("pair_scale"))

    def it_sits_between_the_reference_diff_and_the_cost_section():
        assert SOURCE.index('report("diff")') < SOURCE.index("### port-to-port diff")
        assert SOURCE.index("### port-to-port diff") < SOURCE.index("def _(pair_report):")
        assert SOURCE.index("def _(pair_report):") < SOURCE.index("### cost")

    def it_puts_the_pair_stats_beside_the_port_versus_reference_median():
        body = ast.unparse(function_def("pair_summary"))
        for column in (
            "n_pairs",
            "median_pair_similarity_pct",
            "min_pair_similarity_pct",
            "max_pair_similarity_pct",
            "median_reference_similarity_pct",
        ):
            assert column in body


EXPORT = NOTEBOOK.parent / "export_charts.py"
EXPORT_SOURCE = EXPORT.read_text()


def cell_functions() -> list[ast.FunctionDef]:
    return [
        node
        for cell in ast.parse(SOURCE).body
        if isinstance(cell, ast.FunctionDef)
        for node in cell.body
        if isinstance(node, ast.FunctionDef)
    ]


def chart_builders() -> set[str]:
    return {
        node.name
        for node in cell_functions()
        if any(
            isinstance(call, ast.Call) and ast.unparse(call.func) in ("alt.layer", "alt.concat")
            for call in ast.walk(node)
        )
    }


def notebook_names() -> set[str]:
    return {
        node.slice.value
        for node in ast.walk(ast.parse(EXPORT_SOURCE))
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "notebook"
        and isinstance(node.slice, ast.Constant)
    }


def rendered_sections(renderer: str) -> set[str]:
    return {
        ast.literal_eval(node.args[0])
        for node in ast.walk(ast.parse(SOURCE))
        if isinstance(node, ast.Call) and ast.unparse(node.func) == renderer
    }


def describe_chart_export():
    def it_takes_every_chart_builder_from_the_notebook():
        assert chart_builders() <= notebook_names()

    def it_builds_no_chart_of_its_own():
        modules = {
            alias.name if isinstance(node, ast.Import) else node.module
            for node in ast.walk(ast.parse(EXPORT_SOURCE))
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        assert "altair" not in modules

    def it_exports_every_forward_section_the_notebook_renders():
        keys = {key.value for key in assignment("SECTIONS").keys}
        assert rendered_sections("report") == keys

    def it_exports_every_reverse_section_the_notebook_renders():
        listed = ast.literal_eval(assignment("REVERSE_SECTIONS", EXPORT_SOURCE))
        assert rendered_sections("reverse_report") == set(listed)

    def it_writes_svg_png_and_vega_lite_json():
        formats = ast.literal_eval(assignment("FORMATS", EXPORT_SOURCE))
        assert set(formats) == {".svg", ".png", ".json"}
        assert formats[".png"] == {"scale_factor": 2}
