import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import polars as pl
    from dirsql._dirsql import DirSQL

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
    from src.run_table import completed_runs, reverse_runs_table, runs_table


    ROOT = Path(__file__).resolve().parents[1]
    DATA = ROOT / "packages" / "gbnf-experiment" / "data"
    REVERSE = ROOT / "proposed-projects" / "round-trip-experiment" / "reverse"
    DERIVATION = "af673dbe41be73ce"
    REFERENCE = Path.home() / ".cache" / "ports" / "gbnf-experiment" / "derivations" / DERIVATION / "source"
    EXCLUDE = [
        "node_modules",
        "__pycache__",
        ".venv",
        ".pytest_cache",
        "dist",
        "dev-deps",
        "tests",
        "test",
        "integration-tests",
        "conftest.py",
        "*_test.py",
        "test_*.py",
        "*.test.ts",
        "*.spec.ts",
    ]
    EXCLUDE_BY_LANGUAGE = {"python": EXCLUDE, "typescript": [*EXCLUDE, "builder", "dev"]}

    def codebases_under(root, table):
        # A fresh DirSQL scan every run, so a run banked since the last refresh is picked up.
        db = DirSQL(str(root), tables=[table])
        return [
            Codebase.from_run(
                row,
                exclude=EXCLUDE_BY_LANGUAGE[row["target_language"]],
                reference=REFERENCE / row["target_language"],
            )
            for row in completed_runs(db, table.name)
        ]

    codebases = codebases_under(DATA, runs_table())
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
    PERFORMANCE_METRICS = ["ladder_ref_ratio", "ladder_rungs_completed", "ladder_total_ms"]
    # The reference is timed once per port run, so its total is a run column, not a table column.
    LADDER_REFERENCE_TOTAL = "ladder_reference_total_ms"
    # Read by the performance notes below as prose, so they stay out of the summary tables.
    LADDER_NOTE_METRICS = ["ladder_slope", "ladder_reference_slope", "ladder_reference_rungs"]
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
        *PERFORMANCE_METRICS,
        LADDER_REFERENCE_TOTAL,
        *LADDER_NOTE_METRICS,
    ]

    def metrics_frame(codebases, metrics, flags):
        return pl.DataFrame(
            [
                {**codebase.run, **{metric: getattr(codebase, metric) for metric in metrics}}
                for codebase in codebases
            ],
            schema_overrides={"completed_at": pl.String, "error": pl.String},
        ).with_columns(
            pl.col(flags).cast(pl.Boolean),
            duration=pl.duration(milliseconds=pl.col("duration_ms")),
        )

    runs = metrics_frame(codebases, METRICS, FLAGS)
    reverse_runs = metrics_frame(
        reverse_codebases, REVERSE_METRICS, [*FLAGS, *FORWARD_FLAGS]
    )
    port_pairs = within_direction_similarity(codebases)
    cell_pairs = within_cell(port_pairs)
    return (
        Codebase,
        DIFF_METRICS,
        EMBEDDING_METRICS,
        EXCLUDE_BY_LANGUAGE,
        FORWARD_FLAGS,
        LADDER_REFERENCE_TOTAL,
        LAYOUT_LABELS,
        LAYOUT_RULE,
        PERFORMANCE_METRICS,
        REFERENCE,
        REFERENCE_ID,
        TEST_METRICS,
        alt,
        cell_pairs,
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
    DIFF_METRICS,
    EMBEDDING_METRICS,
    FORWARD_FLAGS,
    LADDER_REFERENCE_TOTAL,
    LAYOUT_LABELS,
    LAYOUT_RULE,
    PERFORMANCE_METRICS,
    REFERENCE_ID,
    TEST_METRICS,
    alt,
    cell_pairs,
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
        "mean_cyclomatic",
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
        "loc": "Lines of code",
        "mean_cyclomatic": "Mean cyclomatic complexity",
        "adapted_unit_pass_pct": "Unit tests passing (%)",
        "adapted_integration_pass_pct": "Integration tests passing (%)",
        "adapted_integration_coverage_pct": "Integration coverage (%)",
        "chamfer_distance": "Embedding distance (chamfer)",
        "chamfer_a_to_b": "Embedding, port to reference",
        "chamfer_b_to_a": "Embedding, reference to port",
        "ladder_ref_ratio": "Ladder time ÷ reference",
        "ladder_rungs_completed": "Ladder rungs completed",
        "ladder_total_ms": "Ladder total (ms)",
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

    def panel_title(text):
        return alt.TitleParams(text, fontSize=11, anchor="start", color=INK)

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
        frame, target_language, source_language, metrics, flags=CONDITION_FLAGS, anchors=None
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
            title=None,
            scale=alt.Scale(paddingInner=BAND_PADDING, paddingOuter=BAND_PADDING / 2),
        )
        # A continuous offset scale is measured from the band's left edge, not its middle,
        # so half a band puts the fan back under the label and on the median tick.
        centre = PANEL_WIDTH / len(conditions(source_language)) * (1 - BAND_PADDING) / 2

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
            points = base.mark_point(filled=True, size=96).encode(
                x=x, xOffset=dot_offset(rows, centre), y=alt.Y("value:Q", scale=scale)
            )
            if metric == DIFF_LEAD:
                points = points.encode(shape=layout_shape())
            rule = (
                base.mark_rule()
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
                width=PANEL_WIDTH, height=height, title=panel_title(metric_title(metric))
            )

        return alt.concat(*(panel(metric) for metric in metrics), columns=4)

    DIFF_LEAD = "reference_diff_similarity_pct"
    UNIT_LEAD = "adapted_unit_pass_pct"
    # A section's lead column gets a chart of its own; the rest fold into an accordion.
    LEAD_COLUMNS = {DIFF_LEAD: "Other diff columns", UNIT_LEAD: "Other test columns"}

    def section_chart(metrics, frame, target_language, source_language, flags=CONDITION_FLAGS):
        def build(columns):
            return chart(frame, target_language, source_language, columns, flags, CALIBRATION)

        lead = next((metric for metric in metrics if metric in LEAD_COLUMNS), None)
        if lead is None:
            return build(metrics)
        # shim_chart draws SHIM_COLUMNS before and after, so the section leaves them to it.
        others = [metric for metric in metrics if metric not in (lead, *SHIM_COLUMNS)]
        return mo.vstack([build([lead]), mo.accordion({LEAD_COLUMNS[lead]: build(others)})])

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
    REFERENCE_LABEL = "hand-written reference"
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

    MATRIX_CELL_PX = 34
    MATRIX_LABEL_PX = 8
    MATRIX_VALUE_PX = 9
    MATRIX_STRIP_PX = 9
    MATRIX_STRIP_GAP = 4
    MUTED_INK = "#898781"
    SURFACE = "#fcfcfb"
    SEQUENTIAL_BLUE = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#0d366b"]
    REFERENCE_TICK = "reference"

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
        """Every off-diagonal cell of the square, each half of a pair marked for its role.

        The diagonal is left out: a port against itself is 100 by definition and would own
        the top of any scale fitted to the data. The measure is symmetric, so a pair is
        printed once, in the lower triangle, and filled once, in the upper.
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
                    "half": "colour" if column > row else "number",
                    "similarity_pct": float(
                        matrix[place[items[row][0]], place[items[column][0]]]
                    ),
                }
                for row in range(len(items))
                for column in range(len(items))
                if row != column
            ]
        )

    def matrix_blocks(ordered):
        """The first item of every block: the four conditions, then the reference alone."""
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

    def pair_matrix_chart(source_language):
        """The 21-item square: values in one triangle, colour in the other, no diagonal."""
        ordered = matrix_ports(source_language)
        items = ordered["port"].to_list()
        cells = matrix_cells(source_language, ordered)
        low = cells["similarity_pct"].min()
        high = cells["similarity_pct"].max()
        side = MATRIX_CELL_PX * len(items)
        scale = alt.Scale(domain=items)
        x = alt.X("port_a:N", scale=scale, title=None, axis=matrix_axis(labelAngle=-90))
        y = alt.Y("port_b:N", scale=scale, title=None, axis=matrix_axis(labelAngle=0)
        filled = (
            alt.Chart(cells.filter(pl.col("half") == "colour"))
            .mark_rect(stroke=SURFACE, strokeWidth=1)
            .encode(
                x=x,
                y=y,
                color=alt.Color(
                    "similarity_pct:Q",
                    title="Similarity (%)",
                    scale=alt.Scale(domain=[low, high], range=SEQUENTIAL_BLUE),
                    legend=alt.Legend(titleFontSize=10, labelFontSize=9, gradientLength=side / 3),
                ),
            )
        )
        printed = (
            alt.Chart(cells.filter(pl.col("half") == "number"))
            .mark_text(fontSize=MATRIX_VALUE_PX, color=INK)
            .encode(x=x, y=y, text=alt.Text("similarity_pct:Q", format=".0f"))
        )
        strip = ordered.select("port", "condition")
        # Both strips share one scale, so only the header draws the key.
        def strip_colour(legend):
            return alt.Color(
                "condition:N",
                scale=alt.Scale(
                    domain=map_labels(source_language), range=[*CONDITION_COLOURS, INK]
                ),
                legend=alt.Legend(title=None, symbolType="square", labelFontSize=9)
                if legend
                else None,
            )
        near, far = MATRIX_STRIP_GAP, MATRIX_STRIP_GAP + MATRIX_STRIP_PX
        header = (
            alt.Chart(strip)
            .mark_rect()
            .encode(
                x=alt.X("port:N", scale=scale, title=None, axis=matrix_axis(labelAngle=-90)),
                y=alt.value(-far),
                y2=alt.value(-near),
                color=strip_colour(True),
            )
        )
        sidebar = (
            alt.Chart(strip)
            .mark_rect()
            .encode(
                y=alt.Y("port:N", scale=scale, title=None, axis=matrix_axis(labelAngle=0),
                x=alt.value(-far),
                x2=alt.value(-near),
                color=strip_colour(False),
            )
        )
        # Thick rules box each 5x5 condition block, and the reference's own rank last.
        blocks = matrix_blocks(ordered)
        closing = pl.DataFrame({"port": [items[-1]]})
        edge = {"color": INK, "strokeWidth": 2, "opacity": 0.75}
        rules = [
            alt.Chart(frame)
            .mark_rule(**edge)
            .encode(**{channel: builder("port:N", scale=scale, bandPosition=position)})
            for frame, position in ((blocks, 0), (closing, 1))
            for channel, builder in (("x", alt.X), ("y", alt.Y))
        ]
        return (
            alt.layer(filled, printed, header, sidebar, *rules)
            .resolve_scale(color="independent")
            .properties(
                width=side,
                height=side,
                title=alt.TitleParams(
                    f"{direction(source_language)}: port against port",
                    subtitle=[
                        "Each cell is one pair: the port on its row read against the port on"
                        " its column. Lower triangle prints the value, upper fills it as"
                        " colour.",
                        "The diagonal is left out, a port against itself being 100. Colour"
                        f" runs over the measured range, {low:.0f}% to {high:.0f}%.",
                        "Strips on both headers carry the condition; the hand-written"
                        " reference takes the last row and column.",
                    ],
                    fontSize=11,
                    subtitleFontSize=10,
                    subtitleColor="#52514e",
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
                *(
                    build(source_language)
                    for build in (focused_chart, anchor_chart, mds_chart, pair_matrix_chart)
                    for source_language in ("python", "typescript")
                ),
            ]
        )

    def ratio_rows(source_language):
        return (
            with_conditions(
                runs.filter(pl.col("source_language") == source_language), source_language
            )
            .select(
                "run_id",
                "condition",
                "ladder_rungs_completed",
                "ladder_total_ms",
                pl.col("ladder_ref_ratio").alias("value"),
                pl.lit(1.0).alias("reference"),
            )
            .with_columns(port=pl.col("run_id").str.slice(-8))
        )

    RATIO_TOLERANCE = 0.01
    RATIO_WIDTH = 440

    def nudges(values, tolerance=RATIO_TOLERANCE):
        """Dots within `tolerance` of each other spread sideways; a dot on its own stays centred."""
        slots = [0.0] * len(values)
        cluster = []

        def spread(cluster):
            for position, index in enumerate(cluster):
                slots[index] = position - (len(cluster) - 1) / 2

        for index in sorted(range(len(values)), key=lambda index: values[index]):
            if cluster and values[index] - values[cluster[-1]] > tolerance:
                spread(cluster)
                cluster = []
            cluster.append(index)
        spread(cluster)
        return slots

    def with_nudges(rows):
        placed = {
            run_id: nudge
            for group in rows.partition_by("condition")
            for run_id, nudge in zip(group["run_id"], nudges(group["value"].to_list()))
        }
        return rows.with_columns(
            nudge=pl.col("run_id").replace_strict(placed, return_dtype=pl.Float64)
        )

    def ratio_domain():
        # One domain for both directions, so the panels can be read against each other.
        return metric_domain(
            runs.select(pl.col("ladder_ref_ratio").alias("value"), pl.lit(1.0).alias("reference"))
        )

    def ratio_chart(source_language, rows):
        rows = with_nudges(rows)
        domain = ratio_domain()
        scale = (
            alt.Scale(zero=False) if domain is None else alt.Scale(domain=list(domain), nice=False)
        )
        y = alt.Y("value:Q", title=metric_title("ladder_ref_ratio"), scale=scale)
        parity = pl.DataFrame({"value": [1.0], "label": ["reference"]})
        x = alt.X(
            "condition:N", sort=[label for label, *_ in conditions(source_language)], title=None
        )
        # A continuous offset scale is measured from the band's left edge, so half a band
        # (the panel's width over the four conditions) re-centres the dots under their label.
        centre = RATIO_WIDTH / len(conditions(source_language)) / 2
        offset = alt.XOffset(
            "nudge:Q",
            scale=alt.Scale(domain=[-2, 2], range=[centre - 24, centre + 24]),
            title=None,
        )
        dots = (
            alt.Chart(rows)
            .mark_point(filled=True, size=70, opacity=0.75)
            .encode(
                x=x,
                xOffset=offset,
                y=y,
                tooltip=[
                    alt.Tooltip("port:N", title="run"),
                    alt.Tooltip("value:Q", title="ladder time ÷ reference", format=".2f"),
                    alt.Tooltip("ladder_rungs_completed:Q", title="rungs completed"),
                    alt.Tooltip("ladder_total_ms:Q", title="total ms", format=",.1f"),
                ],
            )
        )
        # The median rides the same offset scale as the dots, which is anchored to the band's edge.
        medians = median_tick(
            alt.Chart(
                rows.group_by("condition", maintain_order=True).agg(
                    pl.col("value").median(), nudge=pl.lit(0.0)
                )
            ),
            size=56,
            x=x,
            xOffset=offset,
            y=y,
        )
        rule = alt.Chart(parity).mark_rule(color="black", strokeWidth=2).encode(y=y)
        rule_label = (
            alt.Chart(parity)
            .mark_text(align="left", baseline="bottom", dy=-2, fontSize=9)
            .encode(y=y, x=alt.value(2), text="label:N")
        )
        return alt.layer(medians, dots, rule, rule_label).properties(
            width=RATIO_WIDTH,
            height=300,
            title=panel_title(
                f"{direction(source_language)}: ladder time relative to the reference"
            ),
        )

    def performance_panel(source_language):
        by_source = runs.filter(pl.col("source_language") == source_language)
        rows = ratio_rows(source_language)
        failed = rows.filter(pl.col("value").is_null())["port"].sort().to_list()
        reference_total = by_source[LADDER_REFERENCE_TOTAL].median()
        parts = [
            mo.md(
                f"Reference ladder total: {reference_total:,.1f} ms "
                f"(median over {by_source.height} runs)."
            ),
            ratio_chart(source_language, rows.filter(pl.col("value").is_not_null())),
        ]
        if failed:
            parts.append(mo.md(f"Failed every rung: {len(failed)} ({', '.join(failed)})."))
        return mo.vstack(parts)

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
        "performance": (
            PERFORMANCE_METRICS,
            ["timestamp", *PERFORMANCE_METRICS],
            performance_panel,
        ),
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

    return pair_report, report, reverse_report


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
                    A forward run ports one hand-written reference library into the other language. The 40 runs cover eight cells: source language, python reference tests placed in the sandbox or not, typescript reference tests placed in the sandbox or not. Every port is measured against the hand-written reference in its own target language, under the same excludes.

                    The sections below are the mechanical measurements — the reference diff, the port-to-port diff, what the run cost, the size of what it produced, test pass rates. They are read off the runs and the files themselves, with no model involved.
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

                    Ports are compared only against the hand-written reference in the same language, port on `a`, reference on `b`. Model `qwen3-embedding-0.6b-q8_0`, 8192-token context; the largest source file is 10,356 bytes, so nothing is truncated.
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
def _(mo):
    mo.vstack(
        [
            mo.md("""
            ## Performance

            The timing ladder from exercise-api, run over the forward ports only.

            ### performance ladder
            """),
            mo.accordion(
                {
                    "Glossary": mo.md("""
                    A rung is one of the 22 cases in `cases/ladder.jsonl`: eight grammars, each with inputs of growing size, from a one-character literal up to a 64 KB JSON object and JSON nested at six depths.

                    What is timed is `.add(input)` on a freshly constructed `GBNF(grammar)`, with `perf_counter_ns` / `process.hrtime.bigint()`, in one driver process per port.

                    The statistic per rung is the median of that rung's timed passes, in milliseconds. Each case carries its own budget: 3 warm-up and 100 timed passes for the sixteen cases the typescript reference parses in under 100 ms, 1 and 5 for the five that cost it seconds, and a single cold pass for nested depth 8192.

                    The reference is the hand-written library in the port's target language, timed on the same rungs in the same process run as the port it is compared against; it is the black rule at 1.0.

                    Each dot is one port. A rung the port failed (`driver_failed`, timeout, or a raise) carries no timing and drops out of its statistics; a port that failed every rung has no ratio and no dot.

                    - `ladder_ref_ratio`: the median across rungs of the port's per-rung medians, divided by the same median for the reference.
                    - `ladder_rungs_completed`: how many of the 22 rungs produced a timing.
                    - `ladder_total_ms`: the sum of the per-rung medians over the rungs the port completed, in milliseconds.
                    """)
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(report):
    report("performance")
    return


@app.cell(hide_code=True)
def _(pl, reverse_runs, runs):
    DIRECTIONS = [("python", "typescript"), ("typescript", "python")]
    SIMILARITY_FLOOR = 25

    def forward(source_language):
        return runs.filter(pl.col("source_language") == source_language)

    def reference_rungs(frame):
        return [rungs for rungs in frame["ladder_reference_rungs"].to_list() if rungs]

    def median(values):
        return pl.Series(values, dtype=pl.Float64).median()

    def named(frame, column="run_id"):
        # A run is named by the tail of its id here, as it is in the plot above.
        return ", ".join(sorted(value[-8:] for value in frame[column].to_list()))

    def scaling(source_language, target_language):
        frame = forward(source_language)
        slopes = frame["ladder_slope"].drop_nulls()
        reference = frame["ladder_reference_slope"].drop_nulls().median()
        return (
            f"- {source_language} → {target_language}: ports {slopes.min():.2f} to "
            f"{slopes.max():.2f}, reference {reference:.2f}"
        )

    def envelope(source_language, target_language):
        frame = forward(source_language)
        count = median([len(rungs) for rungs in reference_rungs(frame)])
        timed = frame.filter(pl.col("ladder_rungs_completed").is_not_null())
        gaps = sorted(
            completed - count
            for completed in timed["ladder_rungs_completed"].to_list()
            if completed != count
        )
        line = (
            f"- {source_language} → {target_language}: {timed.height - len(gaps)} of "
            f"{timed.height} timed ports completed the reference's {count:.0f} rungs"
        )
        if gaps:
            line += f", {len(gaps)} differed by " + ", ".join(f"{gap:+.0f}" for gap in gaps)
        missing = frame.filter(pl.col("ladder_rungs_completed").is_null())
        if missing.height:
            line += f". No timings at all: {named(missing)}"
        return f"{line}."

    def open_question():
        failed = runs.filter(pl.col("ladder_rungs_completed").is_null())
        weak = reverse_runs.filter(pl.col("reference_diff_similarity_pct") < SIMILARITY_FLOOR)
        both = set(failed["run_id"].to_list()) & set(weak["forward_run_id"].to_list())
        return (
            f"Does speed track fidelity? Failed every rung: {named(failed)}. "
            f"Reverse leg below {SIMILARITY_FLOOR}% `reference_diff_similarity_pct`, "
            f"named by their forward run: {named(weak, 'forward_run_id')}. "
            f"In both: {', '.join(sorted(run_id[-8:] for run_id in both)) or 'none'}."
        )

    performance_notes = "\n\n".join(
        [
            "**Scaling.** The rung-8 log-log slope, the port against the reference timed in "
            "the same run (`ladder_slope`, on `Codebase` and not in the tables above). The "
            "reference figure is the median over the runs in that direction.",
            "\n".join(scaling(*direction) for direction in DIRECTIONS),
            "**Failure envelope.** Rungs completed, the port against the reference's own "
            "count on the same run.",
            "\n".join(envelope(*direction) for direction in DIRECTIONS),
            f"**Open question.** {open_question()}",
        ]
    )
    return (performance_notes,)


@app.cell(hide_code=True)
def _(mo, performance_notes):
    mo.vstack([mo.md("### notes"), mo.accordion({"Notes": mo.md(performance_notes)})])
    return


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

                    There is no performance ladder here: exercise-api has not been run over the reverse ports.
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


if __name__ == "__main__":
    app.run()
