"""Write every chart runs.py renders to analysis/charts, as SVG, PNG and Vega-Lite JSON.

    GENERATE_EMBEDDING_BASE_URL=http://127.0.0.1:8089/v1 uv run --directory analysis python export_charts.py

The charts are the notebook's own objects: app.run() hands back every name a cell
binds, chart builders included, so nothing here rebuilds a chart. The embedding
base url is what the chamfer columns need; without it the notebook raises before
the first chart is built.
"""

from pathlib import Path

import altair as alt
import polars as pl

from runs import app
from src.chart_export import align_panel_titles, fit_pair, share_y_domains, write_chart

CHARTS = Path(__file__).resolve().parent / "charts"
# Blog slots: a 757px body; side-by-side pairs split it with a 1rem (16px) gap. Charts in
# a slot render 1:1 at these widths, so fonts hold one pixel size across the blog.
BODY_WIDTH = 757
HALF_WIDTH = (BODY_WIDTH - 16) / 2
SLOT_WIDTHS = {
    "performance/ladder-ref-ratio-": HALF_WIDTH,
    "statistical-analysis/size-": HALF_WIDTH,
    "statistical-analysis/port-to-port-matrix-": BODY_WIDTH,
}
# Builder widths that land each slot chart just under its slot; fit_pair pads the rest.
SIZE_PANEL_WIDTH = 128.875
SIZE_LABEL_ANGLE = -32.5  # 5 degrees closer to horizontal than the blog's default
# One py->ts run exploded to 146 files (every other run lands at 33-51) and one
# ts->py run to 2,075 LOC; both squash their panels' ranges. The size charts drop
# those runs and carry an asterisk.
SIZE_OUTLIER = (pl.col("file_count") > 100) | (pl.col("loc") > 2000)
MATRIX_SIDE = 598
LANGUAGES = ("python", "typescript")
# The notebook renders reverse_report for these two sections only: there is no reverse ladder.
REVERSE_SECTIONS = ("diff", "embeddings")
GROUPS = {"embeddings": "embeddings", "performance": "performance"}
FORWARD_GROUP = "statistical-analysis"
REVERSE_GROUP = "reverse-ports"
# A section whose lead column is charted alone needs a name for the chart of what is left.
OTHER_COLUMNS = {
    "diff": "reference-diff-other-columns",
    "tests": "adapted-integration-coverage-pct",
}
REVERSE_DIFF_COLUMNS = "reverse-diff-columns"


def slug(name):
    return name.replace("_", "-")


def charts(notebook):
    """Every chart runs.py renders, as (path stem, chart)."""
    for source, target in (("python", "typescript"), ("typescript", "python")):
        yield (
            f"embeddings/port-pairs-{source}-to-{target}",
            notebook["embedding_pair_chart"](
                notebook["embedding_pair_report"]["comparisons"], source, target
            ),
        )
    chart = notebook["chart"]
    calibration = notebook["CALIBRATION"]
    lead = notebook["DIFF_LEAD"]
    leads = notebook["LEAD_COLUMNS"]
    runs = notebook["runs"]
    reverse_runs = notebook["reverse_runs"]
    sections = notebook["SECTIONS"]
    shim = notebook["SHIM_COLUMNS"]

    axis_label_px = notebook["AXIS_LABEL_PX"]
    main_title_px = notebook["MAIN_TITLE_PX"]

    def section_charts(section, metrics, frame, target_language, source_language, flags):
        def build(columns, font_scale=1.0):
            size = (
                {
                    "panel_width": SIZE_PANEL_WIDTH,
                    "axis_label_size": axis_label_px,
                    "x_label_angle": SIZE_LABEL_ANGLE,
                    "panel_title_scale": 0.75,
                    "test_axis": True,
                }
                if section == "size"
                else {}
            )
            return chart(
                frame, target_language, source_language, columns, flags, calibration, font_scale, **size
            )

        section_lead = next((metric for metric in metrics if metric in leads), None)
        if section_lead is None:
            if section == "size":
                built = build(metrics, font_scale=1.5)
                built = built.properties(
                    title=alt.TitleParams(
                        f"{source_language} → {target_language}*",
                        fontSize=main_title_px,
                        anchor="start",
                    )
                )
            else:
                built = build(metrics)
            yield slug(section), built
            return
        # section_chart splits a led section: the lead on its own, the rest in an accordion.
        yield slug(section_lead), build([section_lead])
        yield (
            OTHER_COLUMNS.get(section, slug(section)),
            build([metric for metric in metrics if metric not in (section_lead, *shim)]),
        )

    for source_language in LANGUAGES:
        by_source = runs.filter(pl.col("source_language") == source_language)
        target_language = by_source["target_language"][0]
        direction = f"{source_language}-to-{target_language}"
        for section, (metrics, _display, _extra) in sections.items():
            group = GROUPS.get(section, FORWARD_GROUP)
            if section == "performance":
                rows = notebook["ratio_rows"](source_language)
                yield (
                    f"{group}/ladder-ref-ratio-{direction}",
                    notebook["ratio_chart"](
                        source_language, rows.filter(pl.col("value").is_not_null())
                    ),
                )
                continue
            for name, built in section_charts(
                section,
                metrics,
                by_source.filter(~SIZE_OUTLIER) if section == "size" else by_source,
                target_language,
                source_language,
                notebook["CONDITION_FLAGS"],
            ):
                yield f"{group}/{name}-{direction}", built
        yield (
            f"{FORWARD_GROUP}/shim-integration-pass-pct-{direction}",
            notebook["shim_chart"](source_language),
        )
        yield (
            f"{FORWARD_GROUP}/port-map-focused-{direction}",
            notebook["focused_chart"](source_language),
        )
        yield (
            f"{FORWARD_GROUP}/port-map-anchors-{direction}",
            notebook["anchor_chart"](source_language),
        )
        yield (
            f"{FORWARD_GROUP}/port-map-mds-{direction}",
            notebook["mds_chart"](source_language),
        )
        yield (
            f"{FORWARD_GROUP}/port-to-port-matrix-{direction}",
            notebook["pair_matrix_chart"](source_language, side=MATRIX_SIDE),
        )

    yield f"{FORWARD_GROUP}/port-to-port-similarity-pct", notebook["pair_chart"]()

    for target_language in LANGUAGES:
        by_target = reverse_runs.filter(pl.col("target_language") == target_language)
        if by_target.height == 0:
            continue
        forward_source = by_target["forward_source_language"][0]
        forward_target = by_target["forward_target_language"][0]
        direction = f"{forward_source}-to-{forward_target}-to-{target_language}"
        for section in REVERSE_SECTIONS:
            metrics, _display, _extra = sections[section]
            if section == "diff":
                yield (
                    f"{REVERSE_GROUP}/round-trip-{slug(lead)}-{direction}",
                    notebook["round_trip_chart"](forward_source),
                )
                yield (
                    f"{REVERSE_GROUP}/{REVERSE_DIFF_COLUMNS}-{direction}",
                    chart(
                        by_target,
                        target_language,
                        forward_source,
                        metrics,
                        notebook["FORWARD_FLAGS"],
                        calibration,
                    ),
                )
                continue
            for name, built in section_charts(
                section,
                metrics,
                by_target,
                target_language,
                forward_source,
                notebook["FORWARD_FLAGS"],
            ):
                yield f"{REVERSE_GROUP}/{name}-{direction}", built


def write(chart, stem):
    return write_chart(chart, CHARTS / stem)


def main():
    _outputs, notebook = app.run()
    pending = {}
    for stem, chart in charts(notebook):
        slot = next(
            ((prefix, width) for prefix, width in SLOT_WIDTHS.items() if stem.startswith(prefix)),
            None,
        )
        if slot is None:
            for path in write(chart, stem):
                print(path.relative_to(CHARTS.parent))
        else:
            pending.setdefault(slot, []).append((stem, chart))
    for (prefix, width), group in pending.items():
        specs = [chart.to_dict() for _, chart in group]
        if prefix == "statistical-analysis/size-":
            # The two directions share each panel's y domain so the pair compares by eye.
            specs = share_y_domains(specs)
        fitted = fit_pair(specs, width)
        if prefix == "statistical-analysis/size-":
            # Panel-title dx goes on last, after fit_pair has settled the margins.
            fitted = [align_panel_titles(spec) for spec in fitted]
        for (stem, _), spec in zip(group, fitted):
            for path in write(spec, stem):
                print(path.relative_to(CHARTS.parent))


if __name__ == "__main__":
    main()
