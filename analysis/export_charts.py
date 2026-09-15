"""Write every chart runs.py renders to analysis/charts, as SVG, PNG and Vega-Lite JSON.

    GENERATE_EMBEDDING_BASE_URL=http://127.0.0.1:8089/v1 uv run --directory analysis python export_charts.py

The charts are the notebook's own objects: app.run() hands back every name a cell
binds, chart builders included, so nothing here rebuilds a chart. The embedding
base url is what the chamfer columns need; without it the notebook raises before
the first chart is built.
"""

from pathlib import Path

import polars as pl

from runs import app
from src.chart_export import write_chart

CHARTS = Path(__file__).resolve().parent / "charts"
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
    chart = notebook["chart"]
    calibration = notebook["CALIBRATION"]
    lead = notebook["DIFF_LEAD"]
    leads = notebook["LEAD_COLUMNS"]
    runs = notebook["runs"]
    reverse_runs = notebook["reverse_runs"]
    sections = notebook["SECTIONS"]
    shim = notebook["SHIM_COLUMNS"]

    def section_charts(section, metrics, frame, target_language, source_language, flags):
        def build(columns):
            return chart(frame, target_language, source_language, columns, flags, calibration)

        section_lead = next((metric for metric in metrics if metric in leads), None)
        if section_lead is None:
            yield slug(section), build(metrics)
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
                by_source,
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
            notebook["pair_matrix_chart"](source_language),
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
    for stem, chart in charts(notebook):
        for path in write(chart, stem):
            print(path.relative_to(CHARTS.parent))


if __name__ == "__main__":
    main()
