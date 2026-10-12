import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import altair as alt
    import marimo as mo
    import polars as pl

    from src.Codebase import Codebase
    from src.pair_layout import (
        REFERENCE_ID,
        focused_layout,
        mds_layout,
        medoid_similarity,
        ring_labels,
        ring_points,
        similarity_matrix,
    )
    from src.port_pairs import within_cell, within_direction_similarity
    from src.rebuilt_layout import LAYOUT_LABELS, LAYOUT_RULE, layout_flag
    from src.run_table import V2_FLAGS, is_v2, reverse_runs_table, runs_table


    from src.corpus import (
        DATA, REVERSE, REFERENCE, EXCLUDE_BY_LANGUAGE, codebases_under, runs_under,
    )
    from src.stats import compare, spearman

    all_codebases = codebases_under(DATA, runs_table())
    # The sections below measure V1 runs: V2 runs carry other flags and another target name.
    codebases = [codebase for codebase in all_codebases if not is_v2(codebase.run)]
    # The held-out behavior and API sections measure V2 runs only.
    v2_codebases = [codebase for codebase in all_codebases if is_v2(codebase.run)]
    reverse_codebases = codebases_under(REVERSE, reverse_runs_table())

    FLAGS = ["include_python_tests", "include_typescript_tests", "is_error"]
    FORWARD_FLAGS = ["forward_include_python_tests", "forward_include_typescript_tests"]
    STATIC_METRICS = [
        "file_count",
        "lines",
        "loc",
        "chars",
        "node_count",
        "max_depth",
        "function_count",
        "mean_function_lines",
        "max_function_lines",
        "mean_cyclomatic",
        "max_cyclomatic",
    ]
    TEST_METRICS = [
        "adapted_unit_pass_pct",
        "adapted_integration_pass_pct",
        "adapted_integration_coverage_pct",
        "adapt_rules",
    ]
    # Un-adapted pass rates: forward runs only. The reverse runs have no cached un-adapted
    # report, so asking for one there re-runs the suite.
    PRESHIM_METRICS = ["integration_pass_pct"]
    EMBEDDING_METRICS = ["chamfer_distance", "chamfer_a_to_b", "chamfer_b_to_a"]
    DIFF_METRICS = [
        "reference_diff_similarity_pct",
        "reference_diff_kept_pct",
        "reference_diff_identical",
        "reference_diff_modified",
        "reference_diff_renamed",
        "reference_diff_added",
        "reference_diff_deleted",
    ]
    SHARED_METRICS = [
        *STATIC_METRICS,
        *TEST_METRICS,
        *EMBEDDING_METRICS,
    ]
    REVERSE_METRICS = [*SHARED_METRICS, *DIFF_METRICS]
    METRICS = [
        *SHARED_METRICS,
        *PRESHIM_METRICS,
        *DIFF_METRICS,
    ]

    def metrics_frame(codebases, metrics, flags):
        return pl.DataFrame(
            [
                {**codebase.run, **{metric: getattr(codebase, metric) for metric in metrics}}
                for codebase in codebases
            ],
            # Float even when every value is null, as with no V1 reference below.
            schema_overrides={
                "completed_at": pl.String,
                "error": pl.String,
                **dict.fromkeys(EMBEDDING_METRICS, pl.Float64),
            },
        ).with_columns(
            pl.col(flags).cast(pl.Boolean),
            duration=pl.duration(milliseconds=pl.col("duration_ms")),
        )

    def v1_frames():
        return (
            metrics_frame(codebases, METRICS, FLAGS),
            metrics_frame(reverse_codebases, REVERSE_METRICS, [*FLAGS, *FORWARD_FLAGS]),
        )

    v1_reference_missing = False
    try:
        runs, reverse_runs = v1_frames()
    except RuntimeError as error:
        v1_reference_missing = True
        # The V1 reference source is a cache that can be missing. Without it the V1
        # reference-relative columns are left empty, so the V2 sections still render.
        mo.output.append(mo.callout(mo.md(
            f"V1 reference-relative columns (embeddings, reference diff) are empty: "
            f"`{str(error).splitlines()[0][:300]}`"
        ), kind="warn"))
        for codebase in [*codebases, *reverse_codebases]:
            codebase.reference = None
        runs, reverse_runs = v1_frames()

    def behavior_columns(codebase):
        return {
            "behavior_agreement_pct": codebase.behavior_agreement_pct,
            **{
                f"reference_{reference}_port_{port}": count
                for reference, ports in codebase.behavior_confusion.items()
                for port, count in ports.items()
            },
            "behavior_note": codebase.behavior_note,
        }

    def size_columns(codebase):
        return {"file_count": codebase.file_count, "loc": codebase.loc}

    # Every AST column, in table order, with the title its chart carries.
    AST_TITLES = {
        "ast_matched_fraction": "Share of the reference's functions the port has a counterpart for",
        "ast_tree_edit_median": "Median tree edit distance between paired functions, normalised",
        "ast_branching_wasserstein": "Distance between the port's and the reference's branching distributions",
        "ast_mean_edge_recall": "Share of the reference's call edges the port also makes, mean over entry points",
        "ast_median_trace_normalised": "Edit distance between the reference's and the port's call traces, median over entry points",
        "ast_matched_count": "Functions paired with a reference function",
        "ast_port_only_count": "Port functions with no reference counterpart",
        "ast_reference_only_count": "Reference functions with no port counterpart",
        "ast_median_line_drift": "Median length difference of paired functions in lines, port minus reference",
        "ast_tree_edit_mean": "Mean tree edit distance between paired functions, normalised",
        "ast_api_shared": "Public API entries the port shares with the reference",
        "ast_api_port_only": "Public API entries only the port exports",
        "ast_api_reference_only": "Public API entries only the reference exports",
        "ast_entry_point_count": "Public entry points traced",
        "ast_reachable_fraction_reference": "Share of the reference's functions reachable from an entry point",
        "ast_reachable_fraction_port": "Share of the port's functions reachable from an entry point",
        "ast_unreachable_port_only": "Port functions reachable from no entry point",
        "ast_delta_node_count": "AST nodes, port minus reference",
        "ast_delta_max_depth": "Deepest AST node, port minus reference",
        "ast_delta_function_count": "Functions, port minus reference",
        "ast_delta_mean_function_lines": "Mean function length in lines, port minus reference",
        "ast_delta_max_function_lines": "Longest function in lines, port minus reference",
        "ast_delta_mean_cyclomatic": "Mean cyclomatic complexity, port minus reference",
        "ast_delta_max_cyclomatic": "Highest cyclomatic complexity, port minus reference",
    }

    def ast_columns(codebase):
        report = codebase.ast_report
        if report is None:
            return {**dict.fromkeys(AST_TITLES), "ast_note": codebase.ast_note}
        functions = report["functions"]
        tree_edit = report["tree_edit_distance"]
        call_paths = report["call_paths"]
        api = report["api_surface"]
        return {
            "ast_matched_fraction": functions["matched_fraction"],
            "ast_tree_edit_median": tree_edit["median_normalised"],
            "ast_branching_wasserstein": report["branching"]["wasserstein"],
            "ast_mean_edge_recall": call_paths["mean_edge_recall"],
            "ast_median_trace_normalised": call_paths["median_trace_normalised"],
            "ast_matched_count": functions["matched_count"],
            "ast_port_only_count": functions["port_only_count"],
            "ast_reference_only_count": functions["reference_only_count"],
            "ast_median_line_drift": functions["median_line_drift"],
            "ast_tree_edit_mean": tree_edit["mean_normalised"],
            **{f"ast_api_{side}": len(api[side]) for side in ("shared", "port_only", "reference_only")},
            "ast_entry_point_count": call_paths["entry_point_count"],
            "ast_reachable_fraction_reference": call_paths["reachable_fraction_reference"],
            "ast_reachable_fraction_port": call_paths["reachable_fraction_port"],
            "ast_unreachable_port_only": len(call_paths["unreachable_port_only"]),
            **{
                column: report["delta"][column.removeprefix("ast_delta_")]["delta"]
                for column in AST_TITLES
                if column.startswith("ast_delta_")
            },
            "ast_note": None,
        }

    TRANSCRIPT_LEADS = [
        "read_source_tests",
        "read_target_tests",
        "suite_run_count",
        "own_tests_written",
        "files_read_before_first_write",
        "reread_count",
    ]
    V2_STRINGS = {"completed_at": pl.String, "error": pl.String, "terminal_reason": pl.String}
    v2_runs = pl.DataFrame(
        [
            {
                **codebase.run,
                **size_columns(codebase),
                **behavior_columns(codebase),
                "api_agreement_pct": codebase.api_agreement_pct,
                **ast_columns(codebase),
                **{lead: codebase.transcript[lead] for lead in TRANSCRIPT_LEADS},
            }
            for codebase in v2_codebases
        ],
        # measure-ast's median line drift is an int or a float run to run.
        schema_overrides={
            **V2_STRINGS,
            "behavior_note": pl.String,
            "ast_note": pl.String,
            "ast_median_line_drift": pl.Float64,
            "files_read_before_first_write": pl.Int64,
        },
    )
    v2_ast_explainers = pl.DataFrame(
        [
            {"run_id": codebase.run["run_id"], "explainer": sentence}
            for codebase in v2_codebases
            if codebase.ast_report is not None
            for sentence in codebase.ast_report['call_paths']['explainer']
        ],
        schema={"run_id": pl.String, "explainer": pl.String},
    )
    # Every finished V2 attempt, the non-zero exits the tables above exclude among them.
    v2_attempts = pl.DataFrame(
        [run for run in runs_under(DATA, runs_table(), include_nonzero_exit=True) if is_v2(run)],
        schema_overrides=V2_STRINGS,
    )

    def api_columns(codebase):
        return {
            "api_agreement_pct": codebase.api_agreement_pct,
            **{f"api_{outcome}": count for outcome, count in codebase.api_outcomes.items()},
            **{
                f"api_reference_{reference}_port_{port}": count
                for reference, ports in codebase.api_confusion.items()
                for port, count in ports.items()
            },
            "api_note": codebase.api_note,
        }

    v2_api_runs = pl.DataFrame(
        [{**codebase.run, **api_columns(codebase)} for codebase in v2_codebases],
        schema_overrides={"completed_at": pl.String, "error": pl.String, "api_note": pl.String},
    )
    # The token split by cache tier is left out; the totals around the first write stay.
    # Lists and the per-class last counts are flattened or quoted below.
    TRANSCRIPT_DROPPED = {
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_creation_tokens",
        "suite_runs",
        "last_suite_counts",
        "own_test_files",
        "fetch_commands",
        "differential_evidence",
    }
    SUITE_CLASSES = ["source_tests", "target_tests", "own_tests", "unknown"]

    def transcript_columns(codebase):
        report = codebase.transcript
        evidence = report["differential_evidence"]
        return {
            **{field: value for field, value in report.items() if field not in TRANSCRIPT_DROPPED},
            **{
                f"last_{suite}_{count}": report["last_suite_counts"].get(suite, {}).get(count)
                for suite in SUITE_CLASSES
                for count in ("passed", "failed")
            },
            "differential_evidence": None if evidence is None else evidence.get("command", evidence.get("path")),
            "read_order": " → ".join(report["read_order"]),
        }

    v2_transcript_runs = pl.DataFrame(
        [{**codebase.run, **transcript_columns(codebase)} for codebase in v2_codebases],
        schema_overrides={
            **V2_STRINGS,
            "differential_evidence": pl.String,
            **{f"last_{suite}_{count}": pl.Int64 for suite in SUITE_CLASSES for count in ("passed", "failed")},
            "first_write_turn": pl.Int64,
            "last_suite_run_turn": pl.Int64,
            "tokens_before_first_write": pl.Int64,
            "tokens_after_first_write": pl.Int64,
            "first_read_path": pl.String,
            "first_read_class": pl.String,
            "first_read_is_entry_point": pl.Boolean,
            "files_read_before_first_write": pl.Int64,
            "source_files_read_before_first_write": pl.Int64,
            "max_rereads_path": pl.String,
            "search_calls_per_file_read": pl.Float64,
            "read_order": pl.String,
            "reads_after_last_write": pl.Int64,
        },
    )
    port_pairs = within_direction_similarity(codebases)
    cell_pairs = within_cell(port_pairs)
    return (
        AST_TITLES,
        Codebase,
        DIFF_METRICS,
        EMBEDDING_METRICS,
        EXCLUDE_BY_LANGUAGE,
        FORWARD_FLAGS,
        LAYOUT_LABELS,
        LAYOUT_RULE,
        REFERENCE,
        REFERENCE_ID,
        TEST_METRICS,
        TRANSCRIPT_LEADS,
        V2_FLAGS,
        alt,
        cell_pairs,
        compare,
        focused_layout,
        layout_flag,
        mds_layout,
        medoid_similarity,
        mo,
        pl,
        port_pairs,
        reverse_runs,
        ring_labels,
        ring_points,
        runs,
        similarity_matrix,
        spearman,
        v1_reference_missing,
        v2_api_runs,
        v2_ast_explainers,
        v2_attempts,
        v2_runs,
        v2_transcript_runs,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Reference

    Reference: the hand-written libraries the ports are measured against. Its columns are defined in the size and tests glossaries below.
    """)
    return


@app.cell(hide_code=True)
def _(Codebase, EXCLUDE_BY_LANGUAGE, REFERENCE, mo, pl):
    def reference_row(language):
        codebase = Codebase(
            REFERENCE / language,
            exclude=EXCLUDE_BY_LANGUAGE[language],
            language=language,
            run_id=f"reference-{language}",
        )
        coverage = codebase.adapted_integration_coverage_pct
        return {
            "language": language,
            "file_count": codebase.file_count,
            "loc": codebase.loc,
            "mean_cyclomatic": codebase.mean_cyclomatic,
            "adapted_integration_coverage_pct": coverage,
        }

    reference = pl.DataFrame(
        [
            reference_row(language)
            for language in ("python", "typescript")
            if (REFERENCE / language).exists()
        ],
        schema={
            "language": pl.String,
            "file_count": pl.Int64,
            "loc": pl.Int64,
            "mean_cyclomatic": pl.Float64,
            "adapted_integration_coverage_pct": pl.Float64,
        },
    )
    mo.ui.table(reference.with_columns(pl.col(pl.Float64).round(2)))
    return (reference,)


@app.cell(hide_code=True)
def _(
    AST_TITLES,
    DIFF_METRICS,
    EMBEDDING_METRICS,
    FORWARD_FLAGS,
    LAYOUT_LABELS,
    LAYOUT_RULE,
    REFERENCE_ID,
    TEST_METRICS,
    TRANSCRIPT_LEADS,
    V2_FLAGS,
    alt,
    cell_pairs,
    compare,
    focused_layout,
    layout_flag,
    mds_layout,
    medoid_similarity,
    mo,
    pl,
    port_pairs,
    reference,
    reverse_runs,
    ring_labels,
    ring_points,
    runs,
    similarity_matrix,
    spearman,
    v1_reference_missing,
    v2_api_runs,
    v2_ast_explainers,
    v2_attempts,
    v2_runs,
    v2_transcript_runs,
):
    CONDITION_FLAGS = ["include_python_tests", "include_typescript_tests"]

    def conditions(source_language):
        # Labels name the port's own direction, so the flag order flips with it.
        source_python = source_language == "python"
        return [
            ("no tests", False, False),
            ("source tests", source_python, not source_python),
            ("target tests", not source_python, source_python),
            ("both tests", True, True),
        ]

    COST_COLUMNS = [
        "total_tokens",
        "api_calls",
        "duration",
    ]
    SIZE_COLUMNS = [
        "file_count",
        "loc",
    ]
    TEST_COLUMNS = [
        "adapted_unit_pass_pct",
        "adapted_integration_pass_pct",
        "adapted_integration_coverage_pct",
    ]
    EMBEDDING_COLUMNS = f"^(mean_|median_)?({'|'.join(EMBEDDING_METRICS)})$"
    # Chart titles read as prose, so a chart lifted out of the notebook says what it holds.
    METRIC_TITLES = {
        "reference_diff_similarity_pct": "Similarity to reference (%)",
        "reference_diff_kept_pct": "Reference lines kept (%)",
        "reference_diff_identical": "Files identical",
        "reference_diff_modified": "Files modified",
        "reference_diff_renamed": "Files renamed",
        "reference_diff_added": "Files added",
        "reference_diff_deleted": "Files deleted",
        "total_tokens": "Total tokens",
        "api_calls": "API calls",
        "duration_min": "Duration (minutes)",
        "file_count": "Files",
        "loc": "LOC",
        "mean_cyclomatic": "Mean cyclomatic complexity",
        "adapted_unit_pass_pct": "Unit tests passing (%)",
        "adapted_integration_pass_pct": "Integration tests passing (%)",
        "adapted_integration_coverage_pct": "Integration coverage (%)",
        "chamfer_distance": "Embedding distance (chamfer)",
        "chamfer_a_to_b": "Embedding, port to reference",
        "chamfer_b_to_a": "Embedding, reference to port",
    }
    CALIBRATION = {
        "chamfer_distance": [
            ("reorder", {"python": 0.010, "typescript": 0.005}),
            ("drop10%", {"python": 0.023, "typescript": 0.004}),
            ("rename", {"python": 0.030, "typescript": 0.024}),
            ("rename+reorder", {"python": 0.039, "typescript": 0.027}),
            ("drop25%", {"python": 0.043, "typescript": 0.022}),
            ("rename+reorder+drop10%", {"python": 0.063, "typescript": 0.031}),
        ]
    }

    def subset(frame, python_tests, typescript_tests, flags=CONDITION_FLAGS):
        python_flag, typescript_flag = flags
        return frame.filter(
            (pl.col(python_flag) == python_tests) & (pl.col(typescript_flag) == typescript_tests)
        )

    def with_conditions(frame, source_language, flags=CONDITION_FLAGS):
        return pl.concat(
            subset(frame, python_tests, typescript_tests, flags).with_columns(
                pl.lit(label).alias("condition")
            )
            for label, python_tests, typescript_tests in conditions(source_language)
        )

    def condition_colour(source_language):
        labels = [label for label, *_ in conditions(source_language)]
        return alt.Color("condition:N", sort=labels, scale=alt.Scale(domain=labels), title=None)

    def summary(frame, metrics, source_language, flags=CONDITION_FLAGS):
        return pl.concat(
            subset(frame, python_tests, typescript_tests, flags).select(
                pl.lit(label).alias("condition"),
                pl.len().alias("n"),
                *(
                    expr
                    for metric in metrics
                    for expr in (
                        pl.col(metric).mean().alias(f"mean_{metric}"),
                        pl.col(metric).median().alias(f"median_{metric}"),
                    )
                ),
            )
            for label, python_tests, typescript_tests in conditions(source_language)
        ).with_columns(
            pl.col(pl.Float64).exclude(EMBEDDING_COLUMNS).round(2),
            pl.col(EMBEDDING_COLUMNS).round(3),
        )

    def metric_domain(rows, extra=()):
        values = (
            pl.concat(
                [
                    rows.select(pl.col("value").alias("v")),
                    rows.select(pl.col("reference").alias("v")),
                ]
            )
            .filter(pl.col("v").is_finite())["v"]
            .to_list()
        ) + list(extra)
        if not values:
            return None
        low, high = min(values), max(values)
        # A zero baseline draws every bar the same height once the values
        # cluster, so each panel starts just under its own smallest value.
        span = high - low
        margin = span * 0.08 if span else max(abs(high), 1.0) * 0.02
        return low - margin, high + margin

    def label_levels(rungs, domain, height, gap=11):
        """Anchor labels, pushed apart where the rungs are too close to read."""
        low, high = domain
        step = (high - low) * gap / height
        placed = []
        for rung in sorted(rungs, key=lambda rung: rung["level"]):
            level = rung["level"]
            if placed and level - placed[-1]["level"] < step:
                level = placed[-1]["level"] + step
            placed.append({"label": rung["label"], "level": min(level, high)})
        return placed

    TICK_SIZE = 30
    PANEL_WIDTH = 160
    # Coincident runs fan out DOT_STEP apart, tightened to fit the band the padding pins down.
    BAND_PADDING = 0.25
    DOT_STEP = 6
    BAND_FILL = 0.8
    # One title tier across the blog's charts: the main title at 19.5, panel and axis
    # titles 25% under the size section's old 16.5.
    MAIN_TITLE_PX = 19.5
    AXIS_TITLE_PX = 11 * 1.5 * 0.75
    # X-axis labels match across the blog's charts: the size charts' 15px and the
    # ladder's 20px met at sqrt(15 * 20), so both moved by the same 15.5%.
    AXIS_LABEL_PX = 17.32
    # The x axis is test inclusion; once the axis says so, the labels can stay short.
    TEST_AXIS_TITLE = "test inclusion"
    CONDITION_LABEL_EXPR = (
        "{'no tests': 'none', 'source tests': 'source', "
        "'target tests': 'target', 'both tests': 'both'}[datum.label]"
    )

    def panel_title(text, font_size=11):
        return alt.TitleParams(text, fontSize=font_size, anchor="start", color=INK)

    def metric_title(metric):
        return METRIC_TITLES.get(metric, metric.replace("_", " "))

    def median_tick(base, size=TICK_SIZE, **encodings):
        """The cell's median: an anchor a run in the cell actually sits on, unlike a mean."""
        return base.mark_tick(thickness=2, size=size, color=INK, opacity=0.7).encode(**encodings)

    def fan_out(rows):
        """Each run's place in its stack of coincident values, counted out from zero."""
        stacks = [
            stack.with_columns(nudge=pl.int_range(pl.len()) - (pl.len() - 1) / 2)
            for _value, stack in rows.group_by("condition", "value", maintain_order=True)
        ]
        return pl.concat(stacks) if stacks else rows.with_columns(nudge=pl.lit(0.0))

    def dot_offset(rows, centre):
        """Five runs at one value draw as five dots, and a lone run stays on the centre."""
        half = rows["nudge"].max() or 1.0
        reach = min(half * DOT_STEP, centre * BAND_FILL)
        return alt.XOffset(
            "nudge:Q",
            scale=alt.Scale(domain=[-half, half], range=[centre - reach, centre + reach]),
            title=None,
        )

    def layout_shape():
        return alt.Shape(
            "layout:N",
            scale=alt.Scale(domain=LAYOUT_LABELS, range=["circle", "triangle-up"]),
            legend=alt.Legend(title=["file layout", LAYOUT_RULE], labelLimit=220, titleLimit=260),
        )

    def chart(
        frame,
        target_language,
        source_language,
        metrics,
        flags=CONDITION_FLAGS,
        anchors=None,
        font_scale=1.0,
        panel_width=PANEL_WIDTH,
        axis_label_size=None,
        x_label_angle=None,
        panel_title_scale=1.0,
        test_axis=False,
    ):
        metrics = ["duration_min" if metric == "duration" else metric for metric in metrics]
        labelled = with_conditions(frame, source_language, flags)
        values = (
            labelled.with_columns(
                layout_flag(), duration_min=pl.col("duration").dt.total_milliseconds() / 60_000
            )
            .select("condition", "layout", pl.col(metrics).cast(pl.Float64))
            .unpivot(index=["condition", "layout"], variable_name="metric", value_name="value")
        )
        references = (
            reference.filter(pl.col("language") == target_language)
            .select(pl.exclude("language").cast(pl.Float64))
            .unpivot(variable_name="metric", value_name="reference")
        )
        long = values.join(references, on="metric", how="left", maintain_order="left")
        x = alt.X(
            "condition:N",
            sort=[label for label, *_ in conditions(source_language)],
            scale=alt.Scale(paddingInner=BAND_PADDING, paddingOuter=BAND_PADDING / 2),
            title=TEST_AXIS_TITLE if test_axis else None,
            axis=alt.Axis(
                labelFontSize=axis_label_size or 10 * font_scale,
                # Some charts want the labels flatter than the shared config angle.
                **({"labelAngle": x_label_angle} if x_label_angle is not None else {}),
                **(
                    {"labelExpr": CONDITION_LABEL_EXPR, "titleFontSize": AXIS_TITLE_PX}
                    if test_axis
                    else {}
                ),
            ),
        )
        # A continuous offset scale is measured from the band's left edge, not its middle,
        # so half a band puts the fan back under the label and on the median tick.
        centre = panel_width / len(conditions(source_language)) * (1 - BAND_PADDING) / 2

        def panel(metric):
            rows = fan_out(long.filter(pl.col("metric") == metric))
            rungs = [
                {"label": label, "level": levels[target_language]}
                for label, levels in (anchors or {}).get(metric, [])
            ]
            # An anchored panel is taller: six rungs need the room.
            height = 260 if rungs else 140
            domain = metric_domain(rows, [rung["level"] for rung in rungs])
            scale = (
                alt.Scale(zero=False)
                if domain is None
                else alt.Scale(domain=list(domain), nice=False)
            )
            base = alt.Chart(rows)
            median = median_tick(base, x=x, y=alt.Y("median(value):Q", title=None, scale=scale))
            # Dots: a full-strength ring around a half-strength fill stays readable
            # where the fan's points overlap.
            points = base.mark_point(
                filled=True, size=96, fillOpacity=0.5, stroke="#4c78a8", strokeWidth=2, strokeOpacity=1
            ).encode(
                x=x,
                xOffset=dot_offset(rows, centre),
                y=alt.Y(
                    "value:Q",
                    scale=scale,
                    axis=alt.Axis(
                        labelFontSize=axis_label_size or 10 * font_scale,
                        titleFontSize=11 * font_scale,
                        # LOC counts read better as 1k / 1.5k / 2k.
                        **({"format": "~s"} if metric == "loc" else {}),
                    ),
                ),
            )
            if metric == DIFF_LEAD:
                points = points.encode(shape=layout_shape())
            rule = (
                base.mark_rule(color=REFERENCE_GREY)
                .transform_filter(alt.FieldValidPredicate(field="reference", valid=True))
                .encode(y=alt.Y("median(reference):Q", scale=scale))
            )
            layers = [median, points, rule]
            if rungs:
                level = alt.Y("level:Q", title=None, scale=scale)
                layers.append(
                    alt.Chart(pl.DataFrame(rungs))
                    .mark_rule(strokeDash=[4, 2], color="firebrick", opacity=0.5)
                    .encode(y=level)
                )
                layers.append(
                    alt.Chart(pl.DataFrame(label_levels(rungs, domain, height)))
                    .mark_text(
                        align="right", baseline="bottom", dy=-1, fontSize=8, color="firebrick"
                    )
                    .encode(y=level, x=alt.value(158), text="label:N")
                )
            return alt.layer(*layers).properties(
                width=panel_width,
                height=height,
                title=panel_title(metric_title(metric), 11 * font_scale * panel_title_scale),
            )

        return alt.concat(*(panel(metric) for metric in metrics), columns=4)

    DIFF_LEAD = "reference_diff_similarity_pct"
    UNIT_LEAD = "adapted_unit_pass_pct"
    # A section's lead column gets a chart of its own; the rest fold into an accordion.
    LEAD_COLUMNS = {DIFF_LEAD: "Other diff columns", UNIT_LEAD: "Other test columns"}

    def section_chart(metrics, frame, target_language, source_language, flags=CONDITION_FLAGS):
        def build(columns, font_scale=1.0):
            return chart(
                frame, target_language, source_language, columns, flags, CALIBRATION, font_scale
            )

        lead = next((metric for metric in metrics if metric in LEAD_COLUMNS), None)
        if lead is None:
            if metrics == SIZE_COLUMNS:
                result = build(metrics, font_scale=1.5)
                return result.properties(
                    title=alt.TitleParams(
                        f"{source_language} → {target_language}",
                        fontSize=21,
                        anchor="start",
                    )
                )
            return build(metrics)
        # shim_chart draws SHIM_COLUMNS before and after, so the section leaves them to it.
        others = [metric for metric in metrics if metric not in (lead, *SHIM_COLUMNS)]
        return mo.vstack([build([lead]), mo.accordion({LEAD_COLUMNS[lead]: build(others)})])

    # V2 conditions name which reference suites sat in the sandbox: unit is the source
    # language's unit suite, source and target the integration suites in each language.
    V2_CONDITIONS = [
        ("none", False, False, False),
        ("unit", True, False, False),
        ("source", False, True, False),
        ("target", False, False, True),
        ("unit + source", True, True, False),
        ("unit + target", True, False, True),
        ("source + target", False, True, True),
        ("all", True, True, True),
    ]
    BEHAVIOR_LEAD = "behavior_agreement_pct"
    BEHAVIOR_PANEL_WIDTH = 320
    BEHAVIOR_SOURCES = ["python", "javascript"]

    def with_v2_conditions(frame):
        return pl.concat(
            frame.filter(
                *(pl.col(flag).cast(pl.Boolean) == value for flag, value in zip(V2_FLAGS, values))
            ).with_columns(pl.lit(label).alias("condition"))
            for label, *values in V2_CONDITIONS
        )

    def behavior_title(metric):
        if metric == BEHAVIOR_LEAD:
            return "Held-out behavior agreement with the reference (%)"
        _, reference_outcome, _, port_outcome = metric.split("_")
        verbs = {"accept": "accepts", "reject": "rejects", "error": "errors on", "crash": "crashes on"}
        return f"Pairs the reference {verbs[reference_outcome]} and the port {verbs[port_outcome]}"

    DOT_STROKE = "#4c78a8"
    IQR_OPACITY = 0.25
    IQR_WIDTH = 8

    def n_label_expr(rows, labels):
        """Each band's label over its run count, so every panel says how many runs it holds."""
        counts = dict(rows.group_by("condition").len().iter_rows())
        lookup = ", ".join(f"'{label}': 'n={counts.get(label, 0)}'" for label in labels)
        return f"[datum.label, {{{lookup}}}[datum.label]]"

    def iqr_bar(base, x, scale):
        """The middle half of the cell's runs, drawn behind its dots."""
        return base.mark_rule(strokeWidth=IQR_WIDTH, color=DOT_STROKE, opacity=IQR_OPACITY).encode(
            x=x, y=alt.Y("q1(value):Q", title=None, scale=scale), y2=alt.Y2("q3(value)")
        )

    def behavior_chart(frame, metric=BEHAVIOR_LEAD, *, lead=BEHAVIOR_LEAD, title=behavior_title):
        labels = [label for label, *_ in V2_CONDITIONS]
        labelled = with_v2_conditions(frame)
        centre = BEHAVIOR_PANEL_WIDTH / len(labels) * (1 - BAND_PADDING) / 2

        def panel(source_language):
            by_source = labelled.filter(pl.col("source_language") == source_language)
            values = by_source.select("condition", pl.col(metric).cast(pl.Float64).alias("value"))
            # A run without a value has no dot, so it joins no n either.
            rows = fan_out(values.drop_nulls("value"))
            x = alt.X(
                "condition:N",
                sort=labels,
                scale=alt.Scale(
                    domain=labels, paddingInner=BAND_PADDING, paddingOuter=BAND_PADDING / 2
                ),
                title=TEST_AXIS_TITLE,
                axis=alt.Axis(labelExpr=n_label_expr(rows, labels)),
            )
            base = alt.Chart(rows)
            # Agreement is a percentage, so every panel shares 0 to 100; counts start at zero.
            scale = alt.Scale(domain=[0, 100]) if metric == lead else alt.Scale(zero=True)
            iqr = iqr_bar(base, x, scale)
            median = median_tick(base, x=x, y=alt.Y("median(value):Q", title=None, scale=scale))
            points = base.mark_point(
                filled=True, size=96, fillOpacity=0.5, stroke=DOT_STROKE, strokeWidth=2, strokeOpacity=1
            ).encode(x=x, xOffset=dot_offset(rows, centre), y=alt.Y("value:Q", title=None, scale=scale))
            target_language = by_source["target_language"][0]
            return alt.layer(iqr, median, points).properties(
                width=BEHAVIOR_PANEL_WIDTH,
                height=140,
                title=panel_title(f"{source_language} → {target_language}"),
            )

        present = set(labelled["source_language"])
        return alt.concat(
            *(panel(source) for source in BEHAVIOR_SOURCES if source in present), columns=2
        ).properties(title=alt.TitleParams(title(metric), anchor="start"))

    def behavior_runs(frame):
        return with_v2_conditions(frame).select(
            "run_id",
            "source_language",
            "condition",
            BEHAVIOR_LEAD,
            pl.col("^reference_.+_port_.+$"),
            "behavior_note",
        )

    def behavior_report():
        if v2_runs.height == 0:
            return mo.md("No completed V2 runs.")
        labelled = behavior_runs(v2_runs)
        labels = [label for label, *_ in V2_CONDITIONS]
        summary_table = (
            labelled.group_by("source_language", "condition")
            .agg(
                pl.len().alias("n"),
                pl.col(BEHAVIOR_LEAD).min().alias(f"min_{BEHAVIOR_LEAD}"),
                pl.col(BEHAVIOR_LEAD).median().alias(f"median_{BEHAVIOR_LEAD}"),
                pl.col(BEHAVIOR_LEAD).max().alias(f"max_{BEHAVIOR_LEAD}"),
            )
            .sort(
                pl.col("source_language").cast(pl.Enum(BEHAVIOR_SOURCES)),
                pl.col("condition").cast(pl.Enum(labels)),
            )
            .with_columns(pl.col(pl.Float64).round(2))
        )
        confusion = [column for column in labelled.columns if column.startswith("reference_")]
        return mo.vstack(
            [
                mo.ui.table(summary_table, freeze_columns_left=["source_language", "condition"]),
                behavior_chart(v2_runs),
                mo.accordion(
                    {
                        "Other behavior columns": mo.vstack(
                            [behavior_chart(v2_runs, column) for column in confusion]
                        )
                    }
                ),
                mo.accordion(
                    {
                        f"Runs (n={labelled.height})": mo.ui.table(
                            labelled.with_columns(pl.col(pl.Float64).round(2))
                        )
                    }
                ),
            ]
        )

    API_LEAD = "api_agreement_pct"
    API_OUTCOME_TITLES = {
        "match": "Cases where every step matches and none raised",
        "mismatch": "Cases where the first differing step returned rules on both sides",
        "error_match": "Cases where every step matches and one raised",
        "error_mismatch": "Cases where the first differing step raised on one side",
        "crash": "Cases where either side crashed",
    }

    def api_title(metric):
        if metric == API_LEAD:
            return "Held-out API agreement with the reference (%)"
        if not metric.startswith("api_reference_"):
            return API_OUTCOME_TITLES[metric.removeprefix("api_")]
        _, _, reference_status, _, port_status = metric.split("_")
        verbs = {"ok": "runs without raising", "error": "raises on", "crash": "crashes on"}
        return f"Cases the reference {verbs[reference_status]} and the port {verbs[port_status]}"

    def api_chart(frame, metric=API_LEAD):
        return behavior_chart(frame, metric, lead=API_LEAD, title=api_title)

    def api_runs(frame):
        return with_v2_conditions(frame).select(
            "run_id",
            "source_language",
            "condition",
            API_LEAD,
            # api_calls is the run's own count of model calls, not a measure-api column.
            pl.col("^api_.+$").exclude(API_LEAD, "api_note", "api_calls"),
            "api_note",
        )

    def api_report():
        if v2_api_runs.height == 0:
            return mo.md("No completed V2 runs.")
        labelled = api_runs(v2_api_runs)
        labels = [label for label, *_ in V2_CONDITIONS]
        summary_table = (
            labelled.group_by("source_language", "condition")
            .agg(
                pl.len().alias("n"),
                pl.col(API_LEAD).min().alias(f"min_{API_LEAD}"),
                pl.col(API_LEAD).median().alias(f"median_{API_LEAD}"),
                pl.col(API_LEAD).max().alias(f"max_{API_LEAD}"),
            )
            .sort(
                pl.col("source_language").cast(pl.Enum(BEHAVIOR_SOURCES)),
                pl.col("condition").cast(pl.Enum(labels)),
            )
            .with_columns(pl.col(pl.Float64).round(2))
        )
        others = [
            column
            for column in labelled.columns
            if column.startswith("api_") and column not in (API_LEAD, "api_note")
        ]
        return mo.vstack(
            [
                mo.ui.table(summary_table, freeze_columns_left=["source_language", "condition"]),
                api_chart(v2_api_runs),
                mo.accordion(
                    {
                        "Other API columns": mo.vstack(
                            [api_chart(v2_api_runs, column) for column in others]
                        )
                    }
                ),
                mo.accordion(
                    {
                        f"Runs (n={labelled.height})": mo.ui.table(
                            labelled.with_columns(pl.col(pl.Float64).round(2))
                        )
                    }
                ),
            ]
        )

    AST_LEADS = [
        "ast_matched_fraction",
        "ast_tree_edit_median",
        "ast_branching_wasserstein",
        "ast_mean_edge_recall",
        "ast_median_trace_normalised",
    ]

    def ast_title(metric):
        return AST_TITLES[metric]

    def ast_chart(frame, metric=AST_LEADS[0]):
        # No AST column is a percentage, so every axis starts at zero.
        return behavior_chart(frame, metric, lead=None, title=ast_title)

    def ast_runs(frame):
        return with_v2_conditions(frame).select(
            "run_id",
            "source_language",
            "condition",
            *AST_LEADS,
            pl.col("^ast_.+$").exclude(*AST_LEADS, "ast_note"),
            "ast_note",
        )

    def ast_explainers(frame, explainers):
        """Each run's call-path explainer sentences, labelled by run, source language and condition."""
        runs = with_v2_conditions(frame).select("run_id", "source_language", "condition")
        return {
            f"{run['run_id']} · {run['source_language']} · {run['condition']}": explainers.filter(
                pl.col("run_id") == run["run_id"]
            ).select("explainer")
            for run in runs.iter_rows(named=True)
            if run["run_id"] in explainers["run_id"]
        }

    def ast_report():
        if v2_runs.height == 0:
            return mo.md("No completed V2 runs.")
        labelled = ast_runs(v2_runs)
        labels = [label for label, *_ in V2_CONDITIONS]
        summary_table = (
            labelled.group_by("source_language", "condition")
            .agg(
                pl.len().alias("n"),
                *(
                    getattr(pl.col(lead), statistic)().alias(f"{statistic}_{lead}")
                    for lead in AST_LEADS
                    for statistic in ("min", "median", "max")
                ),
            )
            .sort(
                pl.col("source_language").cast(pl.Enum(BEHAVIOR_SOURCES)),
                pl.col("condition").cast(pl.Enum(labels)),
            )
            .with_columns(pl.col(pl.Float64).round(3))
        )
        others = [column for column in AST_TITLES if column not in AST_LEADS]
        return mo.vstack(
            [
                mo.ui.table(summary_table, freeze_columns_left=["source_language", "condition"]),
                *(ast_chart(v2_runs, lead) for lead in AST_LEADS),
                mo.accordion(
                    {
                        "Other AST columns": mo.vstack(
                            [ast_chart(v2_runs, column) for column in others]
                        )
                    }
                ),
                mo.accordion(
                    {
                        f"Runs (n={labelled.height})": mo.ui.table(
                            labelled.with_columns(pl.col(pl.Float64).round(3))
                        )
                    }
                ),
                mo.accordion(
                    {
                        "Call-path explainer, per run": mo.accordion(
                            {
                                label: mo.ui.table(table, selection=None)
                                for label, table in ast_explainers(v2_runs, v2_ast_explainers).items()
                            }
                        )
                    }
                ),
            ]
        )

    TRANSCRIPT_TITLES = {
        "turns": "Assistant turns",
        "bash_calls": "Bash calls",
        "read_calls": "Read calls",
        "write_calls": "Write calls",
        "edit_calls": "Edit calls",
        "search_calls": "Glob and Grep calls",
        "read_source": "Reads of the source implementation",
        "read_source_tests": "Reads of the source language's shipped tests",
        "read_target_tests": "Reads of the target language's shipped tests",
        "suite_run_count": "Test suite runs",
        "own_tests_written": "Test files the agent wrote itself",
        "fetch_attempts": "Network fetch and install attempts",
        "tokens_before_first_write": "Tokens before the first write into the port",
        "tokens_after_first_write": "Tokens from the first write into the port on",
        "first_write_turn": "Turn of the first write into the port",
        "last_suite_run_turn": "Turn of the last test suite run",
        "files_read_before_first_write": "Files read before the first write into the port",
        "source_files_read_before_first_write": "Source files read before the first write into the port",
        "reread_count": "Reads of a file already read",
        "max_rereads_of_one_file": "Most rereads of one file",
        "search_calls_per_file_read": "Glob and Grep calls per file read",
        "reads_after_last_write": "Reads after the last write into the port",
        **{
            f"last_{suite}_{count}": f"{count.capitalize()} tests in the last run of {name}"
            for suite, name in (
                ("source_tests", "the source language's shipped tests"),
                ("target_tests", "the target language's shipped tests"),
                ("own_tests", "the agent's own tests"),
                ("unknown", "a suite of more than one class"),
            )
            for count in ("passed", "failed")
        },
    }
    # Booleans: the section counts the runs where each holds instead of charting them.
    TRANSCRIPT_COUNTED = ["touched_source_tests", "touched_target_tests", "differential_script"]
    # Counted by value in the first-read table.
    TRANSCRIPT_FIRST_READ = ["first_read_is_entry_point", "first_read_class"]
    FIRST_READ_CLASSES = ["source", "source_tests", "target_tests", "port", "other"]
    # Quoted in the runs table only.
    TRANSCRIPT_QUOTED = ["differential_evidence", "first_read_path", "max_rereads_path", "read_order"]

    def transcript_title(metric):
        return TRANSCRIPT_TITLES[metric]

    def transcript_chart(frame, metric):
        # Counts, never a percentage: no lead takes the 0 to 100 scale.
        return behavior_chart(frame, metric, lead=None, title=transcript_title)

    def transcript_counts(frame):
        return by_cell(
            frame,
            pl.len().alias("n"),
            *(pl.col(column).sum().alias(column) for column in TRANSCRIPT_COUNTED),
        ).with_columns(pl.col("n", *TRANSCRIPT_COUNTED).fill_null(0))

    def first_read_counts(frame):
        # A null entry point: no code file of the source was named by a read.
        entry = pl.col("first_read_is_entry_point")
        return by_cell(
            frame,
            pl.len().alias("n"),
            entry.sum().alias("entry_point"),
            (~entry).sum().alias("not_entry_point"),
            entry.is_null().sum().alias("no_code_file_read"),
            *((pl.col("first_read_class") == cls).sum().alias(f"first_read_{cls}") for cls in FIRST_READ_CLASSES),
        ).with_columns(pl.exclude("source_language", "condition").fill_null(0))

    def transcript_runs(frame):
        others = [column for column in TRANSCRIPT_TITLES if column not in TRANSCRIPT_LEADS]
        return with_v2_conditions(frame).select(
            "run_id",
            "source_language",
            "condition",
            *TRANSCRIPT_LEADS,
            *TRANSCRIPT_COUNTED,
            *TRANSCRIPT_FIRST_READ,
            *others,
            *TRANSCRIPT_QUOTED,
        )

    def transcript_report():
        if v2_transcript_runs.height == 0:
            return mo.md("No completed V2 runs.")
        labelled = transcript_runs(v2_transcript_runs)
        others = [column for column in TRANSCRIPT_TITLES if column not in TRANSCRIPT_LEADS]
        return mo.vstack(
            [
                *(transcript_chart(v2_transcript_runs, lead) for lead in TRANSCRIPT_LEADS),
                mo.ui.table(
                    transcript_counts(v2_transcript_runs),
                    freeze_columns_left=["source_language", "condition"],
                ),
                mo.ui.table(
                    first_read_counts(v2_transcript_runs),
                    freeze_columns_left=["source_language", "condition"],
                ),
                mo.accordion(
                    {
                        "Other transcript columns": mo.vstack(
                            [transcript_chart(v2_transcript_runs, column) for column in others]
                        )
                    }
                ),
                mo.accordion({f"Runs (n={labelled.height})": mo.ui.table(labelled)}),
            ]
        )

    V2_LEADS = [BEHAVIOR_LEAD, API_LEAD, *AST_LEADS, "total_tokens", "loc", *TRANSCRIPT_LEADS]
    V2_SCOPES = ["pooled", *BEHAVIOR_SOURCES]
    # Per-run measures besides held-out behavior; the confusion counts join them from the frame.
    V2_MEASURES = ["total_tokens", "api_calls", "duration_ms", "file_count", "loc", *TRANSCRIPT_LEADS]
    SPEARMAN_CELL_PX = 26
    # red, neutral grey, blue: a diverging ramp whose midpoint reads as no correlation.
    DIVERGING = ["#e34948", "#f0efec", "#2a78d6"]

    def v2_cells():
        """The 16 V2 cells, source language first."""
        labels = [label for label, *_ in V2_CONDITIONS]
        return pl.DataFrame(
            {
                "source_language": [source for source in BEHAVIOR_SOURCES for _ in labels],
                "condition": labels * len(BEHAVIOR_SOURCES),
            }
        )

    def by_cell(frame, *aggregations):
        """One row per V2 cell, every cell present whether or not it has runs."""
        cells = v2_cells()
        if frame.height == 0:
            return cells
        counted = with_v2_conditions(frame).group_by("source_language", "condition").agg(*aggregations)
        return cells.join(counted, on=["source_language", "condition"], how="left", maintain_order="left")

    def lead_title(measure):
        if measure == BEHAVIOR_LEAD:
            return behavior_title(measure)
        if measure in AST_LEADS:
            return ast_title(measure)
        if measure in TRANSCRIPT_LEADS:
            return transcript_title(measure)
        return api_title(measure) if measure == API_LEAD else metric_title(measure)

    def v2_summary(frame, attempts):
        codes = sorted(attempts.filter(pl.col("exit_code") != 0)["exit_code"].unique().to_list())
        excluded = [f"excluded_exit_{code}" for code in codes]
        quartiles = by_cell(
            frame,
            pl.len().alias("n"),
            *(
                expr
                for lead in V2_LEADS
                for expr in (
                    pl.col(lead).quantile(0.25, "linear").alias(f"q1_{lead}"),
                    pl.col(lead).median().alias(f"median_{lead}"),
                    pl.col(lead).quantile(0.75, "linear").alias(f"q3_{lead}"),
                )
            ),
        )
        exits = by_cell(
            attempts,
            *((pl.col("exit_code") == code).sum().alias(name) for code, name in zip(codes, excluded)),
        )
        return (
            quartiles.join(exits, on=["source_language", "condition"], maintain_order="left")
            .with_columns(pl.col("n", *excluded).fill_null(0))
            .select("source_language", "condition", "n", *excluded, pl.exclude("source_language", "condition", "n", *excluded))
        )

    def v2_failures(attempts):
        exits = ["attempts", "exit_0", "exit_137", "api_error"]
        return (
            by_cell(
                attempts,
                pl.len().alias("attempts"),
                (pl.col("exit_code") == 0).sum().alias("exit_0"),
                (pl.col("exit_code") == 137).sum().alias("exit_137"),
                (pl.col("terminal_reason") == "api_error").sum().alias("api_error"),
                pl.col("total_tokens").sum().alias("tokens"),
            )
            .with_columns(pl.col(exits).fill_null(0))
            .with_columns(
                tokens_per_success=pl.when(pl.col("exit_0") > 0).then(
                    pl.col("tokens") / pl.col("exit_0")
                )
            )
            .drop("tokens")
        )

    def flag_comparison(frame, measure):
        """Each flag's on runs against its off runs, pooled and within each source language."""
        rows = []
        for flag in V2_FLAGS:
            on = pl.col(flag).cast(pl.Boolean)
            for scope in V2_SCOPES:
                scoped = frame if scope == "pooled" else frame.filter(pl.col("source_language") == scope)
                result = compare(scoped.filter(on)[measure].to_list(), scoped.filter(~on)[measure].to_list())
                rows.append({"flag": flag, "source_language": scope, **result})
        return pl.DataFrame(rows, schema_overrides={column: pl.Float64 for column in ("median_on", "median_off", "gap", "low", "high", "p", "minimum_detectable_gap")})

    def v2_measures(frame):
        """Every per-run measure the frame carries: both agreements, the AST leads, behavior's confusion counts, cost and size."""
        confusion = [column for column in frame.columns if column.startswith("reference_") and "_port_" in column]
        return [m for m in [BEHAVIOR_LEAD, API_LEAD, *AST_LEADS, *confusion, *V2_MEASURES] if m in frame.columns]

    def varied_measures(frame):
        """The measures that take more than one value; a rank correlation needs a spread."""
        return [m for m in v2_measures(frame) if frame[m].drop_nulls().n_unique() > 1]

    SPEARMAN_READING = (
        "Pooled rows rank both source languages together, though each is measured against a"
        " different reference; the rows for each source language rank within it."
        " The `reference_<a>_port_<b>` counts are the pairs held-out behavior agreement is computed"
        " from, so their correlation with it holds partly by definition."
    )

    def spearman_table(frame):
        """Each varied measure's rank correlation with held-out behavior, pooled and within each source language."""
        tables = []
        for scope in V2_SCOPES:
            scoped = frame if scope == "pooled" else frame.filter(pl.col("source_language") == scope)
            measures = [measure for measure in varied_measures(scoped) if measure != BEHAVIOR_LEAD]
            lead = scoped[BEHAVIOR_LEAD].to_list()
            tables.append(
                pl.DataFrame(
                    {
                        "source_language": [scope] * len(measures),
                        "measure": measures,
                        "rho": [spearman(scoped[measure].to_list(), lead) for measure in measures],
                        "n": [
                            scoped.filter(pl.col(measure).is_not_null() & pl.col(BEHAVIOR_LEAD).is_not_null()).height
                            for measure in measures
                        ],
                    },
                    schema={"source_language": pl.String, "measure": pl.String, "rho": pl.Float64, "n": pl.Int64},
                ).sort(pl.col("rho").abs(), descending=True, nulls_last=True)
            )
        return pl.concat(tables)

    def spearman_matrix(frame):
        measures = varied_measures(frame)
        return pl.DataFrame(
            [
                {"measure_a": a, "measure_b": b, "rho": spearman(frame[a].to_list(), frame[b].to_list())}
                for b in measures
                for a in measures
            ],
            schema={"measure_a": pl.String, "measure_b": pl.String, "rho": pl.Float64},
        )

    def spearman_chart(frame):
        measures = varied_measures(frame)
        side = SPEARMAN_CELL_PX * len(measures)
        x = alt.X("measure_a:N", sort=measures, title=None, axis=alt.Axis(labelAngle=-90, ticks=False, domain=False))
        y = alt.Y("measure_b:N", sort=measures, title=None, axis=alt.Axis(ticks=False, domain=False))
        base = alt.Chart(spearman_matrix(frame))
        cells = base.mark_rect(stroke=SURFACE, strokeWidth=1).encode(
            x=x,
            y=y,
            color=alt.Color(
                "rho:Q",
                title="Spearman ρ",
                # Lab keeps each side on its own hue; the default hcl swings blue through pink.
                scale=alt.Scale(domain=[-1, 0, 1], range=DIVERGING, interpolate="lab"),
                legend=alt.Legend(values=[-1, -0.5, 0, 0.5, 1], format=".1f"),
            ),
            tooltip=[
                alt.Tooltip("measure_a:N", title="measure"),
                alt.Tooltip("measure_b:N", title="against"),
                alt.Tooltip("rho:Q", title="ρ", format=".2f"),
            ],
        )
        # Printed values flip to the page colour where the cell is dark.
        numbers = [
            base.transform_filter(test)
            .mark_text(fontSize=9, color=colour)
            .encode(x=x, y=y, text=alt.Text("rho:Q", format=".2f"))
            for test, colour in (("abs(datum.rho) < 0.6", INK), ("abs(datum.rho) >= 0.6", SURFACE))
        ]
        return alt.layer(cells, *numbers).properties(
            width=side,
            height=side,
            title=alt.TitleParams(
                "How per-run measures rank against each other on V2 runs (Spearman)", anchor="start"
            ),
        )

    FLAG_READING = (
        "Each row sets the runs with the flag on against the runs with it off, pooled over both"
        " source languages and then within each. `gap` is the on median minus the off median."
        " `p` is the share of 10,000 shuffles of the on/off labels (seed 0) whose gap is at least"
        " as far from zero. `low` to `high` is a 95% bootstrap interval on the gap (10,000"
        " resamples, seed 0). `minimum_detectable_gap` is the critical value: an observed gap larger"
        " than it gives p < 0.05 against the same shuffles at this n. A true gap of exactly that size"
        " lands above it only about half the time, so only gaps well beyond it are reliably seen."
        " A row with p ≥ 0.05 reads as a gap too small to see with this n, never as no effect."
    )

    def multiplicity_note(tests):
        """How many flag comparisons this section runs and how many fall below 0.05 by chance alone."""
        return (
            f"This section runs {tests} comparisons with a p, none corrected for the others. If no flag"
            f" changed any measure, about {round(tests * 0.05)} of them would still give p < 0.05."
            " Every p here is exploratory: a lead for a later test, not a confirmed effect."
        )
    V2_NOT_MEASURED = (
        "Reference diff similarity and test pass rates are not measured on V2 runs:"
        " `measure-code-distance` takes no javascript target and `execute-test-suite` finds no V2"
        " suite in the derivation cache."
    )

    def rounded(frame):
        return frame.with_columns(pl.col(pl.Float64).round(2))

    def v2_statistics_report():
        if v2_runs.height == 0:
            return mo.md("No completed V2 runs.")
        cell_columns = ["source_language", "condition"]
        varied = varied_measures(v2_runs)
        constant = [m for m in v2_measures(v2_runs) if m not in varied]
        parts = [
            mo.md("### n, median and interquartile range by cell"),
            mo.ui.table(rounded(v2_summary(v2_runs, v2_attempts)), freeze_columns_left=cell_columns),
            mo.md("### Failures and tokens per successful run"),
            mo.ui.table(rounded(v2_failures(v2_attempts)), freeze_columns_left=cell_columns),
        ]
        comparisons = {measure: flag_comparison(v2_runs, measure) for measure in V2_LEADS}
        tests = sum(table["p"].is_not_null().sum() for table in comparisons.values())
        parts.extend([mo.md("### Per-flag comparison"), mo.md(FLAG_READING), mo.md(multiplicity_note(tests))])
        for measure, table in comparisons.items():
            parts.extend(
                [
                    mo.md(f"#### {lead_title(measure)}"),
                    mo.ui.table(
                        table.with_columns(pl.col(pl.Float64).exclude("p").round(2), pl.col("p").round(4)),
                        freeze_columns_left=["flag", "source_language"],
                    ),
                ]
            )
        parts.extend(
            [
                mo.md(V2_NOT_MEASURED),
                mo.md("### Rank correlation with held-out behavior"),
                mo.md(SPEARMAN_READING),
                mo.ui.table(
                    spearman_table(v2_runs).with_columns(pl.col("rho").round(3)),
                    freeze_columns_left=["source_language", "measure"],
                ),
                spearman_chart(v2_runs),
            ]
        )
        if constant:
            parts.append(mo.md(f"One value across every V2 run, so no rank correlation: {', '.join(constant)}."))
        return mo.vstack(parts)

    PAIR_SERIES = "port vs port"
    REFERENCE_SERIES = "port vs reference"

    def direction(source_language):
        target_language = runs.filter(pl.col("source_language") == source_language)[
            "target_language"
        ][0]
        return f"{source_language} → {target_language}"

    def pair_summary(source_language):
        cells = pl.concat(
            subset(
                cell_pairs.filter(pl.col("source_language") == source_language),
                python_tests,
                typescript_tests,
            ).select(
                pl.lit(direction(source_language)).alias("direction"),
                pl.lit(label).alias("condition"),
                pl.len().alias("n_pairs"),
                pl.col("similarity_pct").median().alias("median_pair_similarity_pct"),
                pl.col("similarity_pct").min().alias("min_pair_similarity_pct"),
                pl.col("similarity_pct").max().alias("max_pair_similarity_pct"),
            )
            for label, python_tests, typescript_tests in conditions(source_language)
        )
        reference_median = summary(
            runs.filter(pl.col("source_language") == source_language),
            [DIFF_LEAD],
            source_language,
        ).select(
            "condition", pl.col(f"median_{DIFF_LEAD}").alias("median_reference_similarity_pct")
        )
        return cells.join(reference_median, on="condition", maintain_order="left")

    def pair_values(source_language):
        by_source = pl.col("source_language") == source_language
        pairs = with_conditions(cell_pairs.filter(by_source), source_language).select(
            "condition",
            pl.lit(PAIR_SERIES).alias("series"),
            pl.col("similarity_pct").alias("value"),
        )
        references = with_conditions(runs.filter(by_source), source_language).select(
            "condition",
            pl.lit(REFERENCE_SERIES).alias("series"),
            pl.col(DIFF_LEAD).cast(pl.Float64).alias("value"),
        )
        return pl.concat([pairs, references])

    def pair_chart():
        def panel(source_language):
            rows = pair_values(source_language)
            domain = metric_domain(rows.with_columns(reference=pl.lit(None, pl.Float64)))
            scale = (
                alt.Scale(zero=False)
                if domain is None
                else alt.Scale(domain=list(domain), nice=False)
            )
            x = alt.X(
                "condition:N",
                sort=[label for label, *_ in conditions(source_language)],
                title=None,
            )
            title = "Similarity (%)"
            y = alt.Y("value:Q", title=title, scale=scale)
            series = alt.Color("series:N", title=None)
            medians = median_tick(
                alt.Chart(rows),
                x=x,
                y=alt.Y("median(value):Q", title=title, scale=scale),
                color=series,
            )
            points = (
                alt.Chart(rows)
                .mark_point(filled=True, size=55, opacity=0.85)
                .encode(x=x, y=y, color=series, shape=alt.Shape("series:N", title=None))
            )
            return alt.layer(medians, points).properties(
                width=300, height=240, title=panel_title(direction(source_language))
            )

        return alt.concat(*(panel(language) for language in ("python", "typescript")), columns=2)

    INK = "#0b0b0b"
    DIAGONAL = "#c3c2b7"
    PAIR_TICKS = [0, 25, 50, 75, 100]
    # blue, orange, aqua, violet: the four condition hues, validated for a scatter's all-pairs
    # separation under deuteranopia, protanopia and tritanopia alike.
    CONDITION_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"]
    CONDITION_SHAPES = ["circle", "square", "triangle-up", "cross"]
    REFERENCE_LABEL = "reference"
    REFERENCE_SHAPE = "diamond"
    RING_LEVELS = [25, 50, 75]
    SCALE_BAR = 20
    PAIR_SIDE = 420

    def pair_scale():
        # Every distribution in this section sits on one fixed axis, so a panel reads
        # against its neighbours and against the absolute number at the same time.
        return alt.Scale(domain=[0, 100], nice=False)

    def pair_ports(source_language):
        """One row per port of this direction: its condition and its similarity to the reference."""
        return (
            with_conditions(
                runs.filter(pl.col("source_language") == source_language), source_language
            )
            .select(
                "run_id",
                "condition",
                pl.col(DIFF_LEAD).cast(pl.Float64).alias("reference_pct"),
            )
            .drop_nulls("reference_pct")
            .with_columns(port=pl.col("run_id").str.slice(-8))
        )

    def pair_similarity(source_language):
        """The direction's ports, and the similarity matrix over them and the reference."""
        ports = pair_ports(source_language)
        measured = port_pairs.filter(
            (pl.col("source_language") == source_language)
            & pl.col("run_id_a").is_in(ports["run_id"])
            & pl.col("run_id_b").is_in(ports["run_id"])
        )
        ids, matrix = similarity_matrix(measured, ports)
        return ports, ids, matrix

    def placed_ports(ports, placed):
        """Layout coordinates against the port they belong to, the reference among them."""
        reference_row = pl.DataFrame(
            {
                "run_id": [REFERENCE_ID],
                "condition": [REFERENCE_LABEL],
                "reference_pct": [100.0],
                "port": [REFERENCE_LABEL],
            }
        ).select(ports.columns)
        return placed.join(
            pl.concat([ports, reference_row]), on="run_id", how="left", maintain_order="left"
        )

    def condition_labels(source_language):
        return [label for label, *_ in conditions(source_language)]

    def map_labels(source_language):
        """The conditions, then the reference, which the two maps place among the ports."""
        return [*condition_labels(source_language), REFERENCE_LABEL]

    # Colour and shape share a domain, so Vega-Lite folds the two legends into one key.
    def map_colour(labels):
        return alt.Color(
            "condition:N",
            sort=labels,
            scale=alt.Scale(domain=labels, range=[*CONDITION_COLOURS, INK][: len(labels)]),
            legend=alt.Legend(title=None, symbolOpacity=1),
        )

    def map_shape(labels):
        return alt.Shape(
            "condition:N",
            sort=labels,
            scale=alt.Scale(
                domain=labels, range=[*CONDITION_SHAPES, REFERENCE_SHAPE][: len(labels)]
            ),
            legend=alt.Legend(title=None, symbolOpacity=1),
        )

    def map_tooltip():
        return [
            alt.Tooltip("port:N", title="port"),
            alt.Tooltip("condition:N", title="condition"),
            alt.Tooltip("reference_pct:Q", title="vs reference %", format=".2f"),
        ]

    def map_domain(rows, reach=0.0, pad=8.0):
        """One domain for both axes: Vega-Lite has no equal-aspect flag, so the numbers give it.

        `reach` is how far from the origin the annotations run, so a ring is not clipped by
        a point cloud that sits inside it.
        """
        low = min(rows["x"].min(), rows["y"].min(), -reach) - pad
        high = max(rows["x"].max(), rows["y"].max(), reach) + pad
        return [low, high]

    def map_axes(rows, reach=0.0):
        blank = alt.Axis(title=None, labels=False, ticks=False, domain=False, grid=False)
        domain = map_domain(rows, reach)
        scale = alt.Scale(domain=domain, nice=False)
        return domain, alt.X("x:Q", scale=scale, axis=blank), alt.Y("y:Q", scale=scale, axis=blank)

    def map_title(source_language, headline, subtitle):
        return alt.TitleParams(
            f"{direction(source_language)}: {headline}",
            subtitle=subtitle,
            fontSize=11,
            subtitleFontSize=10,
            subtitleColor="#52514e",
            anchor="start",
            color=INK,
            offset=8,
        )

    def map_points(rows, source_language, reach=0.0, tooltip=None):
        labels = map_labels(source_language)
        _domain, x, y = map_axes(rows, reach)
        return (
            alt.Chart(rows)
            .mark_point(filled=True, size=90, opacity=0.9)
            .encode(
                x=x,
                y=y,
                color=map_colour(labels),
                shape=map_shape(labels),
                tooltip=tooltip or map_tooltip(),
            )
        )

    def focused_chart(source_language):
        """Every port at its measured distance from the reference; only the angles are fitted."""
        ports, ids, matrix = pair_similarity(source_language)
        placed, residual = focused_layout(ids, matrix)
        rows = placed_ports(ports, placed)
        # The widest ring, so the outermost one is drawn whole even when no port reaches it.
        reach = 100 - min(RING_LEVELS)
        _domain, x, y = map_axes(rows, reach)
        rings = (
            alt.Chart(ring_points(RING_LEVELS))
            .mark_line(color=DIAGONAL, strokeWidth=1)
            .encode(x=x, y=y, detail="ring:N", order="step:Q")
        )
        labels = (
            alt.Chart(ring_labels(RING_LEVELS))
            .mark_text(baseline="bottom", dy=-3, fontSize=9, color="#52514e")
            .encode(x=x, y=y, text="ring:N")
        )
        return alt.layer(rings, labels, map_points(rows, source_language, reach)).properties(
            width=PAIR_SIDE,
            height=PAIR_SIDE,
            title=map_title(
                source_language,
                "ports around the reference",
                [
                    "Distance from the centre is the port's measured similarity to the"
                    " reference, read off the rings.",
                    "Angles are fitted to the port-to-port similarities: residual RMS"
                    f" {residual:.1f} points.",
                ],
            ),
        )

    def anchor_rows(source_language):
        """Each port against the reference and against the medoid of its own condition."""
        ports, ids, matrix = pair_similarity(source_language)
        return ports.join(
            medoid_similarity(ids, matrix, ports), on="run_id", maintain_order="left"
        ).with_columns(medoid_port=pl.col("medoid").str.slice(-8))

    def medoid_caption(rows):
        named = rows.select("condition", "medoid_port").unique(maintain_order=True)
        return "Medoid of each condition: " + ", ".join(
            f"{condition} {medoid}" for condition, medoid in named.iter_rows()
        )

    def anchor_chart(source_language):
        """Two measured axes: the reference on x, the port's own condition medoid on y."""
        rows = anchor_rows(source_language)
        labels = condition_labels(source_language)
        axis = alt.Axis(values=PAIR_TICKS, labelFontSize=10)
        x = alt.X(
            "reference_pct:Q",
            title="Similarity to the hand-written reference (%)",
            scale=pair_scale(),
            axis=axis,
        )
        y = alt.Y(
            "medoid_similarity_pct:Q",
            title="Similarity to this port's condition medoid (%)",
            scale=pair_scale(),
            axis=axis,
        )
        corners = pl.DataFrame(
            {"reference_pct": [0.0, 100.0], "medoid_similarity_pct": [0.0, 100.0]}
        )
        diagonal = (
            alt.Chart(corners).mark_line(color=DIAGONAL, strokeWidth=1).encode(x=x, y=y)
        )
        marker = (
            alt.Chart(corners.tail(1).with_columns(text=pl.lit("y = x")))
            .mark_text(align="right", baseline="top", dx=-4, dy=4, fontSize=9, color=INK)
            .encode(x=x, y=y, text="text:N")
        )
        points = (
            alt.Chart(rows.drop_nulls("medoid_similarity_pct"))
            .mark_point(filled=True, size=90, opacity=0.85)
            .encode(
                x=x,
                y=y,
                color=map_colour(labels),
                shape=map_shape(labels),
                tooltip=[
                    *map_tooltip(),
                    alt.Tooltip("medoid_port:N", title="its medoid"),
                    alt.Tooltip("medoid_similarity_pct:Q", title="vs medoid %", format=".2f"),
                ],
            )
        )
        return alt.layer(diagonal, marker, points).properties(
            width=PAIR_SIDE,
            height=PAIR_SIDE,
            title=map_title(
                source_language,
                "against the reference and against the condition medoid",
                [
                    "Both axes are measured similarity, nothing is fitted. A medoid carries"
                    " no point of its own.",
                    medoid_caption(rows),
                ],
            ),
        )

    def mds_chart(source_language):
        """Metric MDS over all 21 items, with a scale bar because the axes carry no units."""
        ports, ids, matrix = pair_similarity(source_language)
        placed, stress = mds_layout(ids, matrix)
        rows = placed_ports(ports, placed)
        domain, x, y = map_axes(rows)
        corner = domain[0] + (domain[1] - domain[0]) * 0.06
        bar = pl.DataFrame({"x": [corner], "x2": [corner + SCALE_BAR], "y": [corner]})
        rule = (
            alt.Chart(bar)
            .mark_rule(color=INK, strokeWidth=2)
            .encode(x=x, x2=alt.X2("x2"), y=y)
        )
        label = (
            alt.Chart(bar.with_columns(text=pl.lit(f"{SCALE_BAR} similarity points")))
            .mark_text(align="left", baseline="bottom", dy=-4, fontSize=9, color=INK)
            .encode(x=x, y=y, text="text:N")
        )
        return alt.layer(rule, label, map_points(rows, source_language)).properties(
            width=PAIR_SIDE,
            height=PAIR_SIDE,
            title=map_title(
                source_language,
                "MDS map of the 21",
                [
                    "Metric MDS over the measured distances: normalized stress"
                    f" {stress:.3f}.",
                    f"The axes carry no units, so the bar spans {SCALE_BAR} similarity points.",
                ],
            ),
        )

    # Compact cells leave room for readable run labels around the matrix.
    MATRIX_CELL_PX = 30
    MATRIX_LABEL_PX = 13
    MATRIX_STRIP_PX = 9
    MATRIX_STRIP_GAP = 4
    MUTED_INK = "#898781"
    # The reference rule reads on both the light page and the dark variant; a mid-grey
    # sits between the two themes, so dark_spec leaves it alone.
    REFERENCE_GREY = "#6e6e6e"
    SURFACE = "#fcfcfb"
    SEQUENTIAL_BLUE = ["#eef5fd", "#86b6ef", "#3987e5", "#256abf", "#0d366b"]
    REFERENCE_TICK = "reference"
    # A fixed domain, not the data's own range: one outlier row at 1.2% would pin the
    # floor and push the port-port and port-reference medians onto the same shade.
    # Clamping keeps the tails on the ramp's ends.
    MATRIX_DOMAIN = [25, 85]
    # Printed values flip colour at the ramp's midpoint.
    MATRIX_MIDPOINT = sum(MATRIX_DOMAIN) / 2
    # The blog caps the figure at its 637.6px text column, so an SVG px arrives at
    # 637.6/757 of its size. 11 here lands just over 9 on the page.
    MATRIX_VALUE_PX = 11

    def matrix_ports(source_language):
        """The direction's 21 items in axis order: condition, then run id, reference last.

        A port's tick is the 8-character suffix its run id already carries, the same
        abbreviation the maps use, so one port reads as one id on every chart and every
        export. The reference belongs to no condition and takes the last rank of its own.
        """
        ordered = pl.concat(
            block.sort("run_id")
            for _label, block in pair_ports(source_language).group_by(
                "condition", maintain_order=True
            )
        )
        reference_row = pl.DataFrame(
            {
                "run_id": [REFERENCE_ID],
                "condition": [REFERENCE_LABEL],
                "reference_pct": [100.0],
                "port": [REFERENCE_TICK],
            }
        ).select(ordered.columns)
        return pl.concat([ordered, reference_row])

    def matrix_cells(source_language, ordered):
        """Every cell of the upper triangle, coloured.

        The diagonal is left out: a port against itself is 100 by definition and would own
        the top of any scale fitted to the data. The measure is symmetric, so the colour
        carries the whole story and nothing below the diagonal is drawn at all.
        """
        _ports, ids, matrix = pair_similarity(source_language)
        place = {run_id: position for position, run_id in enumerate(ids)}
        items = list(ordered.select("run_id", "port", "condition").iter_rows())
        return pl.DataFrame(
            [
                {
                    "port_a": items[column][1],
                    "port_b": items[row][1],
                    "condition_a": items[column][2],
                    "condition_b": items[row][2],
                    "similarity_pct": float(
                        matrix[place[items[row][0]], place[items[column][0]]]
                    ),
                }
                for row in range(len(items))
                for column in range(len(items))
                if column > row
            ]
        )

    def matrix_blocks(ordered):
        """The first item of every condition block."""
        return (
            ordered.group_by("condition", maintain_order=True).first().select("port", "condition")
        )

    def matrix_axis(**extra):
        # The reference anchors the comparison and belongs to no condition, so its tick is
        # inked and bold where the ports stay muted.
        reference = f"datum.label === '{REFERENCE_TICK}'"
        return alt.Axis(
            labelFontSize=MATRIX_LABEL_PX,
            labelColor=alt.ExprRef(expr=f"{reference} ? '{INK}' : '{MUTED_INK}'"),
            labelFontWeight=alt.ExprRef(expr=f"{reference} ? 'bold' : 'normal'"),
            labelPadding=MATRIX_STRIP_PX + MATRIX_STRIP_GAP * 2,
            ticks=False,
            domain=False,
            **extra,
        )

    def pair_matrix_chart(source_language, side=None):
        """The 21-item square: values in one triangle, colour in the other, no diagonal."""
        target_language = runs.filter(pl.col("source_language") == source_language)[
            "target_language"
        ][0]
        ordered = matrix_ports(source_language)
        items = ordered["port"].to_list()
        cells = matrix_cells(source_language, ordered)
        # 598px of cells fills the blog's 757px body once axes and the legend join in.
        side = side or MATRIX_CELL_PX * len(items)
        # Cells exist only above the diagonal, so the first column and the last row would
        # sit as blank boxed strips: each axis drops its empty end.
        x_scale = alt.Scale(domain=items[1:])
        y_scale = alt.Scale(domain=items[:-1])
        x = alt.X("port_a:N", scale=x_scale, title=None, axis=matrix_axis(labelAngle=-90))
        y = alt.Y("port_b:N", scale=y_scale, title=None, axis=matrix_axis(labelAngle=0))
        filled = (
            alt.Chart(cells)
            .mark_rect(stroke=SURFACE, strokeWidth=1)
            .encode(
                x=x,
                y=y,
                color=alt.Color(
                    "similarity_pct:Q",
                    title="Similarity (%)",
                    scale=alt.Scale(domain=MATRIX_DOMAIN, range=SEQUENTIAL_BLUE, clamp=True),
                    legend=alt.Legend(
                        titleFontSize=10,
                        labelFontSize=9,
                        gradientLength=side / 3,
                        values=[25, 50, 75, 85],
                    ),
                ),
            )
        )
        strip = ordered.select("port", "condition")
        # Each strip covers its own axis's items.
        header_strip = strip.filter(pl.col("port").is_in(items[1:]))
        sidebar_strip = strip.filter(pl.col("port").is_in(items[:-1]))
        # Both strips share one scale, so only the header draws the key.
        def strip_colour(legend):
            return alt.Color(
                "condition:N",
                # The reference belongs to no condition, so it takes a neutral rather than
                # a fifth category colour. dark_spec lifts MUTED_INK for the dark page.
                scale=alt.Scale(
                    domain=map_labels(source_language), range=[*CONDITION_COLOURS, MUTED_INK]
                ),
                legend=alt.Legend(title=None, symbolType="square", labelFontSize=9)
                if legend
                else None,
            )
        near, far = MATRIX_STRIP_GAP, MATRIX_STRIP_GAP + MATRIX_STRIP_PX
        header = (
            alt.Chart(header_strip)
            .mark_rect()
            .encode(
                x=alt.X("port:N", scale=x_scale, title=None, axis=matrix_axis(labelAngle=-90)),
                y=alt.value(-far),
                y2=alt.value(-near),
                color=strip_colour(True),
            )
        )
        sidebar = (
            alt.Chart(sidebar_strip)
            .mark_rect()
            .encode(
                y=alt.Y("port:N", scale=y_scale, title=None, axis=matrix_axis(labelAngle=0)),
                x=alt.value(-far),
                x2=alt.value(-near),
                color=strip_colour(False),
            )
        )
        # Every filled cell carries its number. The colour flips at the ramp's midpoint,
        # and each half is its own layer because dark_spec rewrites a mark's colour but
        # not a conditional's payload.
        numbers = [
            alt.Chart(half)
            .mark_text(fontSize=MATRIX_VALUE_PX, color=colour)
            .encode(x=x, y=y, text=alt.Text("similarity_pct:Q", format=".0f"))
            for half, colour in (
                (cells.filter(pl.col("similarity_pct") < MATRIX_MIDPOINT), INK),
                (cells.filter(pl.col("similarity_pct") >= MATRIX_MIDPOINT), SURFACE),
            )
            if not half.is_empty()
        ]
        # Thick rules box each condition block, each axis's rules running over that
        # axis's items and closing at its last one.
        edge = {"color": INK, "strokeWidth": 2, "opacity": 0.75}
        rules = [
            alt.Chart(frame)
            .mark_rule(**edge)
            .encode(**{channel: builder("port:N", scale=axis_scale, bandPosition=position)})
            for channel, builder, axis_scale, axis_items in (
                ("x", alt.X, x_scale, items[1:]),
                ("y", alt.Y, y_scale, items[:-1]),
            )
            for frame, position in (
                (matrix_blocks(ordered.filter(pl.col("port").is_in(axis_items))), 0),
                (pl.DataFrame({"port": [axis_items[-1]]}), 1),
            )
        ]
        return (
            alt.layer(filled, header, sidebar, *numbers, *rules)
            .resolve_scale(color="independent")
            .properties(
                width=side,
                height=side,
                title=alt.TitleParams(
                    f"{source_language} → {target_language}",
                    fontSize=14,
                    subtitleFontSize=10,
                    anchor="start",
                    color=INK,
                    offset=MATRIX_STRIP_PX + MATRIX_STRIP_GAP * 2 + 6,
                ),
            )
        )

    def pair_report():
        return mo.vstack(
            [
                mo.ui.table(
                    pl.concat(
                        pair_summary(source_language)
                        for source_language in ("python", "typescript")
                    ).with_columns(pl.col(pl.Float64).round(2)),
                    freeze_columns_left=["direction"],
                ),
                pair_chart(),
                # The port maps place each port by its similarity to the V1 reference.
                *(
                    build(source_language)
                    for build in (
                        () if v1_reference_missing
                        else (focused_chart, anchor_chart, mds_chart, pair_matrix_chart)
                    )
                    for source_language in ("python", "typescript")
                ),
            ]
        )

    def shim_rules(frame, source_language):
        fired = pl.col("adapt_rules").str.len_chars() > 0
        return pl.concat(
            subset(frame, python_tests, typescript_tests).select(
                pl.lit(label).alias("condition"),
                fired.sum().alias("ports_with_adapt_rules"),
                pl.col("adapt_rules")
                .filter(fired)
                .str.split(",")
                .explode(empty_as_null=False)
                .unique()
                .sort()
                .str.join(", ")
                .alias("adapt_rules"),
            )
            for label, python_tests, typescript_tests in conditions(source_language)
        )

    SHIM_BEFORE = "before the shim"
    SHIM_AFTER = "after the shim"
    SHIM_SERIES = [SHIM_BEFORE, SHIM_AFTER]
    SHIM_COLUMNS = {
        "integration_pass_pct": SHIM_BEFORE,
        "adapted_integration_pass_pct": SHIM_AFTER,
    }
    SHIM_WIDTH = 440
    SHIM_SLOT = 20

    def shim_rows(source_language):
        long = (
            with_conditions(
                runs.filter(pl.col("source_language") == source_language), source_language
            )
            .select("run_id", "condition", pl.col(list(SHIM_COLUMNS)).cast(pl.Float64))
            .unpivot(index=["run_id", "condition"], variable_name="metric", value_name="value")
            .drop_nulls("value")
            .with_columns(
                series=pl.col("metric").replace_strict(SHIM_COLUMNS),
                port=pl.col("run_id").str.slice(-8),
            )
        )
        # fan_out stacks coincident values within a condition, so each series is fanned alone.
        return pl.concat(
            fan_out(long.filter(pl.col("series") == series)) for series in SHIM_SERIES
        )

    def shim_chart(source_language):
        rows = shim_rows(source_language)
        # A continuous offset is measured from the band's left edge, and the median tick pins
        # paddingInner at BAND_PADDING, so half the drawn band is the centre the slots sit around.
        centre = SHIM_WIDTH / len(conditions(source_language)) * (1 - BAND_PADDING) / 2
        slots = {SHIM_BEFORE: centre - SHIM_SLOT, SHIM_AFTER: centre + SHIM_SLOT}
        slot = pl.col("series").replace_strict(slots, return_dtype=pl.Float64)
        placed = rows.with_columns(offset=slot + pl.col("nudge") * DOT_STEP)
        medians = (
            placed.group_by("condition", "series", maintain_order=True)
            .agg(pl.col("value").median())
            .with_columns(offset=slot)
        )
        x = alt.X(
            "condition:N",
            sort=[label for label, *_ in conditions(source_language)],
            title=None,
            scale=alt.Scale(paddingInner=BAND_PADDING, paddingOuter=BAND_PADDING / 2),
        )
        offset = alt.XOffset(
            "offset:Q",
            scale=alt.Scale(domain=[0, centre * 2], range=[0, centre * 2]),
            title=None,
        )
        # A pass rate runs 0 to 100 whatever the data does, and pre-shim sits on both ends,
        # so the domain is fixed with room for a dot to clear the axis.
        y = alt.Y(
            "value:Q",
            title=metric_title("adapted_integration_pass_pct"),
            scale=alt.Scale(domain=[-5, 105], nice=False),
        )
        colour = alt.Color(
            "series:N",
            sort=SHIM_SERIES,
            scale=alt.Scale(domain=SHIM_SERIES, range=[CONDITION_COLOURS[1], CONDITION_COLOURS[0]]),
            legend=alt.Legend(title=None, symbolOpacity=1),
        )
        dots = (
            alt.Chart(placed)
            .mark_point(filled=True, size=55, opacity=0.85)
            .encode(
                x=x,
                xOffset=offset,
                y=y,
                color=colour,
                tooltip=[
                    alt.Tooltip("port:N", title="run"),
                    alt.Tooltip("series:N", title=None),
                    alt.Tooltip("value:Q", title="passing (%)", format=".1f"),
                ],
            )
        )
        ticks = median_tick(alt.Chart(medians), size=24, x=x, xOffset=offset, y=y, color=colour)
        return alt.layer(ticks, dots).properties(
            width=SHIM_WIDTH,
            height=300,
            title=panel_title(
                f"{direction(source_language)}: integration tests passing, "
                "before and after the shim"
            ),
        )

    def tests_panel(source_language):
        by_source = runs.filter(pl.col("source_language") == source_language)
        target_language = by_source["target_language"][0]
        return mo.vstack(
            [
                section_chart(TEST_COLUMNS, by_source, target_language, source_language),
                shim_chart(source_language),
                mo.ui.table(
                    shim_rules(by_source, source_language), freeze_columns_left=["condition"]
                ),
            ]
        )

    SECTIONS = {
        "cost": (COST_COLUMNS, ["timestamp", *COST_COLUMNS], None),
        "size": (SIZE_COLUMNS, ["timestamp", *SIZE_COLUMNS], None),
        "tests": (TEST_COLUMNS, ["timestamp", *TEST_METRICS], tests_panel),
        "diff": (DIFF_METRICS, ["timestamp", *DIFF_METRICS], None),
        "embeddings": (EMBEDDING_METRICS, ["timestamp", *EMBEDDING_METRICS], None),
    }

    def report(section):
        metrics, display, extra = SECTIONS[section]
        parts = []
        for source_language in ("python", "typescript"):
            by_source = runs.filter(pl.col("source_language") == source_language)
            target_language = by_source["target_language"][0]
            parts.extend(
                [
                    mo.md(f"#### {source_language} → {target_language}"),
                    mo.ui.table(
                        summary(by_source, metrics, source_language),
                        freeze_columns_left=["condition"],
                    ),
                    extra(source_language)
                    if extra is not None
                    else section_chart(metrics, by_source, target_language, source_language),
                ]
            )
            for label, python_tests, typescript_tests in conditions(source_language):
                condition = subset(by_source, python_tests, typescript_tests)
                if condition.height == 0:
                    parts.append(mo.md(f"{label}: no completed runs."))
                    continue
                parts.append(
                    mo.accordion(
                        {
                            f"{label} (n={condition.height})": mo.ui.table(
                                condition.select(display).with_columns(
                                    pl.col(pl.Float64).exclude(EMBEDDING_COLUMNS).round(2),
                                    pl.col(EMBEDDING_COLUMNS).round(3),
                                )
                            )
                        }
                    )
                )
        return mo.vstack(parts)

    ROUND_TRIP_LEGS = ["forward", "reverse"]

    def round_trip_rows(forward_source):
        legs = with_conditions(
            reverse_runs.filter(pl.col("forward_source_language") == forward_source),
            forward_source,
            FORWARD_FLAGS,
        ).select(
            "forward_run_id",
            "condition",
            pl.col(DIFF_LEAD).alias("reverse"),
            layout_flag().alias("reverse_layout"),
        )
        return legs.join(
            runs.select(
                pl.col("run_id").alias("forward_run_id"),
                pl.col(DIFF_LEAD).alias("forward"),
                layout_flag().alias("forward_layout"),
            ),
            on="forward_run_id",
            maintain_order="left",
        ).with_columns(port=pl.col("forward_run_id").str.slice(-8))

    def round_trip_chart(forward_source):
        rows = round_trip_rows(forward_source)
        long = pl.concat(
            rows.with_columns(
                pl.lit(leg).alias("leg"),
                pl.col(leg).alias("value"),
                pl.col(f"{leg}_layout").alias("layout"),
            )
            for leg in ROUND_TRIP_LEGS
        )
        x = alt.X(
            "condition:N",
            sort=[label for label, *_ in conditions(forward_source)],
            title=None,
        )
        offset = alt.XOffset("leg:N", scale=alt.Scale(domain=ROUND_TRIP_LEGS), title=None)
        scale = alt.Scale(domain=[0, 100], nice=False)
        title = metric_title(DIFF_LEAD)
        y = alt.Y("value:Q", title=title, scale=scale)
        base = alt.Chart(long)
        links = base.mark_line(strokeWidth=0.7, color="grey", opacity=0.7).encode(
            x=x, xOffset=offset, y=y, detail=alt.Detail("forward_run_id:N")
        )
        medians = median_tick(
            base,
            size=44,
            x=x,
            xOffset=offset,
            y=alt.Y("median(value):Q", title=title, scale=scale),
        )
        dots = base.mark_point(filled=True, size=60, opacity=0.85).encode(
            x=x,
            xOffset=offset,
            y=y,
            color=alt.Color("leg:N", scale=alt.Scale(domain=ROUND_TRIP_LEGS), title=None),
            shape=layout_shape(),
            tooltip=[
                alt.Tooltip("port:N", title="forward run"),
                alt.Tooltip("condition:N", title="forward condition"),
                alt.Tooltip("forward:Q", title="forward", format=".2f"),
                alt.Tooltip("reverse:Q", title="reverse", format=".2f"),
                alt.Tooltip("layout:N", title="file layout"),
            ],
        )
        return alt.layer(links, medians, dots).properties(
            width=440,
            height=300,
            title=panel_title(f"{title}: each run's forward and reverse leg"),
        )

    def reverse_diff_panel(metrics, by_target, target_language, forward_source):
        return mo.vstack(
            [
                round_trip_chart(forward_source),
                mo.accordion(
                    {
                        "Reverse leg on its own, every diff column": chart(
                            by_target,
                            target_language,
                            forward_source,
                            metrics,
                            FORWARD_FLAGS,
                            CALIBRATION,
                        )
                    }
                ),
            ]
        )

    def reverse_report(section):
        metrics, display, _extra = SECTIONS[section]
        parts = []
        for target_language in ("python", "typescript"):
            by_target = reverse_runs.filter(pl.col("target_language") == target_language)
            if by_target.height == 0:
                parts.append(mo.md(f"#### → {target_language}: no completed reverse runs."))
                continue
            forward_source = by_target["forward_source_language"][0]
            forward_target = by_target["forward_target_language"][0]
            parts.extend(
                [
                    mo.md(f"#### {forward_source} → {forward_target} → {target_language}"),
                    mo.ui.table(
                        summary(by_target, metrics, forward_source, FORWARD_FLAGS),
                        freeze_columns_left=["condition"],
                    ),
                    reverse_diff_panel(metrics, by_target, target_language, forward_source)
                    if section == "diff"
                    else section_chart(
                        metrics, by_target, target_language, forward_source, FORWARD_FLAGS
                    ),
                ]
            )
            for label, python_tests, typescript_tests in conditions(forward_source):
                condition = subset(by_target, python_tests, typescript_tests, FORWARD_FLAGS)
                if condition.height == 0:
                    parts.append(mo.md(f"forward {label}: no completed reverse runs."))
                    continue
                parts.append(
                    mo.accordion(
                        {
                            f"forward {label} (n={condition.height})": mo.ui.table(
                                condition.select("forward_run_id", *display).with_columns(
                                    pl.col(pl.Float64).exclude(EMBEDDING_COLUMNS).round(2),
                                    pl.col(EMBEDDING_COLUMNS).round(3),
                                )
                            )
                        }
                    )
                )
        return mo.vstack(parts)

    return (
        api_report,
        ast_chart,
        ast_report,
        behavior_report,
        pair_report,
        report,
        reverse_report,
        spearman_chart,
        transcript_report,
        v2_statistics_report,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "How to read": mo.md("""
                Condition labels name which reference test suites were placed in the sandbox with the source. Each summary table shows, per condition, `n` runs and the mean and median of every other column over those runs (`mean_` and `median_` prefixes); the individual runs are in the accordion for each condition. Size columns are defined in the cost glossary. The chart shows each run as a point, the per-condition median as a short tick, and the reference library's value for the target language as a rule where one exists. There are no bars: a mean bar draws a level no run in the cell need sit at.
                """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## Statistical analysis"),
            mo.accordion(
                {
                    "How to read": mo.md("""
                    V2 is the current study: 16 cells, 2 source languages (python → javascript, javascript → python) × 3 test flags (`include_unit_tests`, `include_source_integration_tests`, `include_target_integration_tests`), 12 runs per cell, claude-opus-5-5 at medium effort. A run that exited non-zero (killed with 137, or an api_error) is left out of every V2 table and chart and counted in the failure table. The V2 sections are the last five: Held-out behavior, Held-out API, AST relative to the reference, Transcripts and V2 statistics. Every V2 chart draws each run as a dot, the cell's median as a tick, its interquartile range as a faint bar, and n under each label.

                    The sections in between are V1: 40 runs in eight cells (source language, python reference tests in the sandbox or not, typescript reference tests in the sandbox or not). Each V1 port is measured against the hand-written reference in its own target language, under the same excludes: the reference diff, the port-to-port diff, cost, size, test pass rates. They are read off the runs and the files, with no model involved.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### reference diff"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    A `git diff` from the hand-written reference in the port's target language to the port. Both trees are copied and normalized the same way before the diff: comments stripped, blank lines dropped, then `ruff format` and an import sort for python, `prettier` for typescript, which does not sort imports. The diff runs with git's rename detection, so a file that moved to a new path is paired with its old one rather than counted as one deletion and one addition.

                    - `reference_diff_similarity_pct`: Dice similarity over normalized lines, `100 × 2 × shared / (reference_lines + port_lines)`, where `shared` is the reference lines the diff leaves untouched. 100 is byte-identical after normalization, 0 shares no line. It is the ratio difflib's `SequenceMatcher.ratio` computes.
                    - `reference_diff_kept_pct`: percent of the reference's normalized lines the diff leaves untouched, `100 × (reference_lines − deletions) / reference_lines`. It ignores what the port added.
                    - `reference_diff_identical`: files at the same relative path on both sides with no diff between them.
                    - `reference_diff_modified`: files at the same relative path on both sides that differ.
                    - `reference_diff_renamed`: files git paired across a change of path.
                    - `reference_diff_added`: files in the port with no counterpart in the reference.
                    - `reference_diff_deleted`: files in the reference with no counterpart in the port.

                    The same excludes apply as everywhere else.
                    """),
                    "How to read": mo.md("""
                    On the `reference_diff_similarity_pct` chart the dot's shape marks the port's file layout. A port counts as having rebuilt the layout when it kept under 10 of the reference's files at their own path — `reference_diff_identical + reference_diff_modified < 10`. That count is 0 to 3 for the ports the rule flags and 25 to 35 for the rest, so any floor between the two picks out the same runs. It flags 4 of the 20 python → typescript runs and 3 of the 20 typescript → python runs.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("diff")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### port-to-port diff"),
            mo.accordion(
                {
                    "How to read": mo.md("""
                    The measure defined in the reference diff note above, taken between two ports instead of between a port and the reference: a `git diff` from one port to the other, both normalized the same way, under the same excludes, read as `similarity_pct`. Both sides are ports into the same target language.

                    A cell is one direction and one condition, so both ports in a pair were produced from the same source language with the same test suites in the sandbox. Five runs per cell make ten unordered pairs; the measure is symmetric, so each pair is measured once. Forward runs only.

                    - `n_pairs`: unordered pairs in the cell.
                    - `median_pair_similarity_pct`, `min_pair_similarity_pct`, `max_pair_similarity_pct`: over the cell's ten pairs.
                    - `median_reference_similarity_pct`: the `median_reference_diff_similarity_pct` of the same cell, carried over from the section above.

                    The chart has one panel per direction: each pair as a point and the cell's median as a short tick, with the five port-versus-reference values on the same axis as a second series.

                    Four scatter plots under it draw every pair of the direction's twenty ports rather than only the pairs inside a cell, in two versions of the same design, one chart per direction each. A point is one port read against one other port: 380 of them per chart, since a pair is drawn once from each of its two ports and the two land at different places. Both axes are fixed 0-100.

                    Read a point by its position. Horizontally: how similar the port the point belongs to is to the hand-written reference, the `reference_diff_similarity_pct` of the section above. Vertically: how similar that port is to the one it is compared with. The grey diagonal is `y = x`, where the two numbers are equal, so a point above it is closer to the compared port than to the reference and a point below it is closer to the reference.

                    Colour is the condition the point's own port ran under, the one on the horizontal axis. Shape is the compared port: in the first version, its own condition, one of the same four; in the second version, only whether it is the same condition as the point's port or a different one, drawn larger where it is the same. Points are drawn part-transparent, so a darker patch is several points on top of each other. Hover a point for both run ids, both conditions, and both numbers.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(pair_report):
    pair_report()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### cost"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    What the run itself cost, whatever it produced.

                    - `total_tokens`: every prompt and every output across all of the run's API calls (`api_calls`), summed, from the transcript, cache ignored.
                    - `duration`: wall clock of the run, from result.json.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("cost")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### size"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    What the run produced, measured on the files themselves.

                    - `file_count`: files left after the exclude patterns (tests, build output, dependency dirs; for typescript also `builder/` and `dev/`).
                    - `loc`: pygount `code_count`: every counted file's lines minus blank, comment, docstring and string-only lines, and lines holding only punctuation such as a lone `}` or a bare `pass`.
                    - `mean_cyclomatic`: 1 plus the branch points in a function's own body, nested functions excluded, averaged over every function.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("size")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### tests"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    - `adapted_unit_pass_pct` / `adapted_integration_pass_pct`: percent of the reference test suite passing when run against the port on the host through the `--adapt` shim (`execute-test-suite --adapt`), which patches four API-shape gaps before running the suite: default export (typescript), flat module layout, `ParseState + str`, exception equality (python). Unit is every test file except the grammar fixtures test; integration is the grammar fixtures test alone. `adapt_rules` lists which rules fired per run, comma-joined; empty when none fired.
                    - `adapted_integration_coverage_pct`: percent of the port's own source lines executed while the integration suite runs against it, measured by coverage.py for python and `@vitest/coverage-v8` for typescript, with the port's own test files excluded. The Reference table carries the same measure taken on each hand-written reference under its own suite.

                    - `integration_pass_pct`: the same integration suite run without `--adapt`, so the port has to match the reference's API shape unaided. Forward runs only.

                    The unit pass rate has a chart of its own and the coverage sits in the accordion beneath it. Below those, one chart per direction puts `integration_pass_pct` and `adapted_integration_pass_pct` side by side in each condition, one dot per run, so the adapted pass rate is charted there and nowhere else. Under the charts is the shim table: `ports_with_adapt_rules` counts the runs in the condition that needed at least one rule, and `adapt_rules` lists the distinct rules that fired across them.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("tests")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("""
            ## Embeddings

            This section is the model-based distance: files become vectors from a code embedding model, and the port is scored on how far its files sit from the reference's.

            ### embeddings
            """),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    Each counted file has its comments stripped and becomes one vector from a code embedding model. For every file in the port we take the cosine distance to its nearest reference file — 0 is identical meaning, 1 unrelated — and average those distances weighted by file length: `chamfer_a_to_b`. `chamfer_b_to_a` is the same walk from the reference's side, `chamfer_distance` the mean of the two. A file with no counterpart is charged its distance to whatever is nearest, so missing or extra files raise the number.

                    For scale, the same measure taken on 2026-09-10 against mutated copies of the references themselves:

                    | mutation | python | typescript |
                    | --- | --- | --- |
                    | unchanged copy | 0.000 | 0.000 |
                    | every definition reordered | 0.010 | 0.005 |
                    | 10% of files deleted | 0.023 | 0.004 |
                    | every identifier renamed | 0.030 | 0.024 |
                    | renamed and reordered | 0.039 | 0.027 |
                    | 25% of files deleted | 0.043 | 0.022 |
                    | renamed, reordered, 10% deleted | 0.063 | 0.031 |

                    The dashed rules on the `chamfer_distance` panels are the six mutation rungs from that table, each drawn at the value for the panel's language.

                    A consistent rename costs as much as deleting a quarter of the files, so this embedder is largely measuring vocabulary, and the number cannot tell "every file slightly different" from "most files exact and a few unrelated". Read it as a relative distance between ports, not a fidelity grade.

                    The per-port panels compare against the hand-written reference in the same language, port on `a`, reference on `b`. The all-pairs panel compares every unordered pair of forward ports within each direction, including across test conditions. Model `qwen3-embedding-0.6b-q8_0`, 8192-token context; the largest source file is 10,356 bytes, so nothing is truncated.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("embeddings")
    return


@app.cell(hide_code=True)
def _(codebases, mo):
    from export_embedding_pairs import pair_chart as embedding_pair_chart
    from src.embedding_pairs import compare_corpus

    skipped = []
    try:
        embedding_pair_report = compare_corpus(codebases)
    except (TypeError, ValueError, OSError) as error:
        # The V1 reference source is missing (see the warning at the top); no pairs.
        skipped = [mo.callout(mo.md(f"Embedding pairs skipped: `{str(error)[:300]}`"), kind="warn")]
        embedding_pair_report = {"comparisons": []}
    mo.vstack([
        *skipped,
        mo.md("### Every port to every port\nAll pairs within each direction, across test conditions. Lower distance means closer. Pairs share ports and are not independent observations."),
        *[embedding_pair_chart(embedding_pair_report["comparisons"], source, target)
          for source, target in (("python", "typescript"), ("typescript", "python"))],
    ])
    return embedding_pair_chart, embedding_pair_report

@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## Reverse ports"),
            mo.accordion(
                {
                    "How to read": mo.md("""
                    A reverse run sends a banked port back through the same harness into the language it came from: the forward run's `ported_implementation` is the source, and the target language is the forward run's source language. So a python → typescript forward run has a typescript → python reverse run.

                    The reverse condition is constant. Both reference test suites are always placed in the sandbox, whatever the forward run's condition was, and `--model` and `--effort` are the forward run's own. The tables therefore vary only by the forward run's condition, which is what each group below is keyed on, and every row names the forward run it came from.

                    Each reverse port is measured against the hand-written reference library in its own target language — the same reference the forward runs into that language are measured against, and the same excludes. The columns mean exactly what they mean in the forward sections above.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### reference diff"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    The measure defined in the forward reference diff note above, with the reverse port on one side and the hand-written reference in the reverse target language on the other. That reference is the library the forward run started from, so here the diff closes the round trip.
                    """),
                    "How to read": mo.md("""
                    The chart pairs each run's two legs: the forward port's `reference_diff_similarity_pct` against the hand-written reference in the forward target language, and its reverse port's against the hand-written reference in the language it started from. One line joins the two legs of one run, so the drop or climb across the round trip is the slope of that line. Both panels use the same 0 to 100 axis.

                    The x axis is the *forward* run's condition. The reverse leg's own condition is constant: every reverse leg ran with both reference suites in the sandbox, whatever the forward run's condition was. So the like-for-like comparison, the one where both legs saw the same tests, is the `both tests` cell; in every other cell the reverse leg had test suites the forward leg did not.

                    The dot's shape marks the file layout of the leg it stands for, under the rule stated in the forward reference diff note: a leg counts as having rebuilt the layout when it kept under 10 of the reference's files at their own path. It flags 0 of the 20 reverse legs into python and 3 of the 20 reverse legs into typescript; the forward legs on the same chart carry the counts from the forward section.

                    The reverse leg's diff columns on their own, including the same similarity column charted per condition, are in the accordion under the chart.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(reverse_report):
    reverse_report("diff")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("### embeddings"),
            mo.accordion(
                {
                    "How to read": mo.md("""
                    The dashed rules on the `chamfer_distance` panel are the calibration rungs from the forward embeddings note above.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(reverse_report):
    reverse_report("embeddings")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## Held-out behavior"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    Held out: the measure-behavior corpus, 100 generated grammars and 799 inputs, never mounted into any agent container. Not either test suite.

                    measure-behavior loads the port, runs every grammar and input pair through it, one process per pair, and records `accept`, `reject`, `error` or `crash`. The hand-written reference in the same language ran the same pairs. A javascript port loads through the typescript driver from `src/index.ts`; a port without one crashes on every pair.

                    - `behavior_agreement_pct`: percent of pairs where the port's outcome matches the reference's.
                    - `reference_<a>_port_<b>`: pairs where the reference's outcome is `a` and the port's is `b`.
                    - `behavior_note`: the first error, when every pair crashed.
                    """),
                    "How to read": mo.md("""
                    V2 runs only. The x axis is test inclusion: `unit` is the source language's unit suite, `source` and `target` the integration suites in the source and target language. Each dot is a run; the tick is the condition's median, the faint bar its interquartile range, and the number under each label its n.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(behavior_report):
    behavior_report()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## Held-out API"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    Held out: the measure-api corpus, 100 generated grammars and 999 cases, never mounted into any agent container. Not either test suite.

                    measure-api steps each case through the port's public API, one process per case: `construct` is `GBNF(grammar)`, `whole` is `add(input)`, then the input added one code point at a time for its first 16. Each step records the rules returned or the class and `pos` of what it raised. The hand-written reference in the same language ran the same cases. A javascript port loads through the typescript driver from `src/index.ts`; a port without one crashes on every case.

                    - `api_agreement_pct`: percent of cases where every step equals the reference's (`match` plus `error_match`).
                    - `api_match`: every step equal, none raised.
                    - `api_mismatch`: the first unequal step returned rules on both sides.
                    - `api_error_match`: every step equal, at least one raised.
                    - `api_error_mismatch`: the first unequal step raised on at least one side, or is missing on one side.
                    - `api_crash`: either side crashed.
                    - `api_reference_<a>_port_<b>`: cases where the reference's status is `a` and the port's is `b`; a status is `crash`, `error` when any step raised, else `ok`.
                    - `api_note`: the first crash, when every case crashed.
                    """),
                    "How to read": mo.md("""
                    V2 runs only. The x axis is test inclusion: `unit` is the source language's unit suite, `source` and `target` the integration suites in the source and target language. Each dot is a run; the tick is the condition's median.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(api_report):
    api_report()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## AST relative to the reference"),
            mo.md("V2 runs only: a python port is compared with the pinned python reference, a javascript port with the pinned javascript reference; reverse ports have no reference here beyond that pin and are not measured."),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    measure-ast `compare` parses the port and the reference at the gbnf pin (with the gbnf-prepare patches) with tree-sitter, under the same excludes, a javascript port with the typescript grammar. Every number measures structural drift from the reference, not fidelity.

                    - `ast_matched_fraction`: reference functions paired with a port function, over the reference's named functions. Functions pair by name, normalised (`_`, `#` and case dropped), and arity.
                    - `ast_tree_edit_median`, `ast_tree_edit_mean`: median and mean over pairs of the Zhang-Shasha tree edit distance between the two functions' syntax trees, labelled by node type alone, over the larger tree's node count. 0 is the same shape; renaming is free.
                    - `ast_branching_wasserstein`: Wasserstein-1 distance between the port's and the reference's per-function cyclomatic numbers.
                    - `ast_matched_count`, `ast_port_only_count`, `ast_reference_only_count`: functions paired, and named functions on one side only.
                    - `ast_median_line_drift`: median over pairs of port lines minus reference lines.
                    - `ast_api_shared`, `ast_api_port_only`, `ast_api_reference_only`: public API entries (`name/arity`) on both sides or one.
                    - `ast_delta_<field>`: port minus reference for each one-tree measure (node count, depth, function count, function lines, cyclomatic).
                    - Call paths, after Sean Goedecke's [How to read code](https://www.seangoedecke.com/how-to-read-code/): each side's calls are followed from every public entry point the two share (a shared function, or a shared class's constructor and public methods), anything outside the package a black box. A call resolves by normalised name when its argument count fits; a method call through any object resolves by name alone; calls through `super`, functions passed as values and implicit calls (operators, iteration) do not resolve.
                    - `ast_mean_edge_recall`: per entry point, the share of the reference's caller-to-callee edges the port also has, by normalised names; mean over entry points whose reference trace has an edge.
                    - `ast_median_trace_normalised`: per entry point, the edit distance between the reference's and the port's depth-first call traces (each function once, callees in call-site order), over the longer trace; median over entry points. 0 is the same path.
                    - `ast_entry_point_count`: entry points traced, on either side.
                    - `ast_reachable_fraction_reference`, `ast_reachable_fraction_port`: named functions reachable from any entry point, over all named functions on that side.
                    - `ast_unreachable_port_only`: port functions reachable from no entry point.
                    - Call-path explainer: one sentence per entry point, `entry: reference trace of n (functions in order); port m, missing caller->callee, extra caller->callee`.
                    - `ast_note`: measure-ast's error when compare exited non-zero, such as a port with no parsable file; the other columns are empty.
                    """),
                    "How to read": mo.md("""
                    The x axis is test inclusion, as in the held-out sections. Each dot is a run, the tick the condition's median, the faint bar its interquartile range, and n sits under each label. One chart per lead; the rest are under "Other AST columns".
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(ast_report):
    ast_report()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## Transcripts"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    measure-transcript reads each run's Claude Code transcript, subagents included, and counts what the agent did. Every column is a count, a turn number or a quoted command. In the sandbox the reference sits at `/input/python` and `/input/javascript` and the port at `/target`. The shipped tests are `/input/python/tests/` and colocated `*_test.py` for python, `/input/javascript/integration-tests/` and colocated `*.test.ts` for javascript. A copy keeps its origin's class until the agent writes the file whole.

                    - `read_source_tests`, `read_target_tests`, `read_source`: Read calls and `cat`, `head`, `less`, `grep`, `sed -n` commands that reach the source language's shipped tests, the target language's shipped tests, or the rest of the source implementation.
                    - `suite_run_count`: commands that run a test suite (pytest, vitest, jest, `node --test`, `npm test`, `pnpm test`, `just test*`).
                    - `own_tests_written`: test files the agent wrote under `/target` and did not copy from `/input`.
                    - `touched_source_tests`, `touched_target_tests`: any read, write, search, command argument or suite run reached that suite. In the table, the runs in the cell where it holds.
                    - `differential_script`: a command or written file runs both python and node, or names both a reference path and a port path. In the table, the runs in the cell where it holds; `differential_evidence` quotes the first.
                    - `turns`: assistant messages. `bash_calls`, `read_calls`, `write_calls`, `edit_calls`, `search_calls` (Glob and Grep): tool calls.
                    - `fetch_attempts`: WebFetch and WebSearch calls and `curl`, `wget`, `pip install`, `npm install` commands. The sandbox has no network; these count the attempts.
                    - `tokens_before_first_write`, `tokens_after_first_write`: input, cache and output tokens summed over the turns before the first write into `/target` and from it on.
                    - `first_write_turn`, `last_suite_run_turn`: the turn of the first write into `/target` and of the last suite run.
                    - `last_<class>_passed`, `last_<class>_failed`: the pass and fail counts of the last suite run of that class whose summary line was read; `unknown` is a run that reached more than one class.
                    - Reading order. A read is one path named by a Read call or a reading command, as written: a glob or a `for f in ...; do cat $f` loop is one read of its pattern. `first_read_path`, `first_read_class`: the first read. `read_order`: source paths in order of first read. `first_read_is_entry_point`: the first source code file read is `gbnf/__init__.py` (python) or `src/index.ts` (javascript); in the second table, `no_code_file_read` when reads name none. `files_read_before_first_write`, `source_files_read_before_first_write`: distinct paths read before the first write into `/target`. `reread_count`: reads of a path already read; `max_rereads_of_one_file`, `max_rereads_path`: the most reread one. `search_calls_per_file_read`: Glob and Grep calls per distinct path read. `reads_after_last_write`: reads after the last write into `/target`.
                    """),
                    "How to read": mo.md("""
                    V2 runs only. The x axis is test inclusion: `unit` is the source language's unit suite, `source` and `target` the integration suites in the source and target language. Each dot is a run; the tick is the condition's median, the faint bar its interquartile range, and the number under each label its n. A run without a value (no write, no suite run of that class) has no dot and is not in the n.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(transcript_report):
    transcript_report()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("## V2 statistics"),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    - `n`: exit-0 runs in the cell. `excluded_exit_<code>`: runs in the cell that exited with that code, left out of every V2 table and chart.
                    - `q1_`, `median_`, `q3_`: the 25th, 50th and 75th percentiles over the cell's runs; `q1` to `q3` is the interquartile range, the middle half of the runs.
                    - `attempts`: every finished run in the cell. `exit_0`, `exit_137`: runs that exited with that code. `api_error`: runs whose result has `terminal_reason` `api_error`.
                    - `tokens_per_success`: every token the cell spent, failed attempts included, divided by its exit-0 runs.
                    - `n_on`, `n_off`, `median_on`, `median_off`, `gap`, `p`, `low`, `high`, `minimum_detectable_gap`: see the per-flag comparison.
                    - `rho`: Spearman rank correlation, the Pearson correlation of the two measures' ranks (ties share their average rank), from −1 to 1. `n`: runs with both measures present.
                    """),
                    "How to read": mo.md("""
                    V2 exit-0 runs only. The lead measures are held-out behavior agreement, held-out API agreement, the three AST leads, total tokens, LOC, and six transcript counts: reads of the source language's shipped tests, reads of the target language's shipped tests, test suite runs, test files the agent wrote itself, files read before the first write into the port, and reads of a file already read. The rank correlation table sets every per-run measure against held-out behavior agreement, so a cheap measure can be checked against it on this data; the heatmap shows every pair.
                    """),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(v2_statistics_report):
    v2_statistics_report()
    return


if __name__ == "__main__":
    app.run()
