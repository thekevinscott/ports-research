"""Export all forward port embedding comparisons without an embedding server.

uv run --directory analysis python export_embedding_pairs.py
"""

import json
import statistics
from pathlib import Path

import altair as alt

from src.corpus import DATA, codebases_under
from src.embedding_pairs import compare_corpus
from src.run_table import runs_table

OUT = Path(__file__).resolve().parent / "charts" / "embeddings"


def pair_chart(rows, source, target):
    selected = [r for r in rows if r["source_language"] == source and r["target_language"] == target]
    labels = {(False, False): "no tests", (True, False): "source tests",
              (False, True): "target tests", (True, True): "both tests"}
    chart_rows = []
    for row in selected:
        if row["comparison"] == "port-to-reference":
            condition = labels[(row["include_python_tests_a"], row["include_typescript_tests_a"])]
            chart_rows.append({"condition": condition, "series": "port vs reference",
                               "value": row["chamfer_distance"]})
        elif (row["include_python_tests_a"], row["include_typescript_tests_a"]) == (row["include_python_tests_b"], row["include_typescript_tests_b"]):
            condition = labels[(row["include_python_tests_a"], row["include_typescript_tests_a"])]
            chart_rows.append({"condition": condition, "series": "port vs port",
                               "value": row["chamfer_distance"]})
    data = alt.Data(values=chart_rows)
    x = alt.X("condition:N", sort=list(labels.values()), title=None)
    y_title = "Weighted Chamfer distance (lower = closer)"
    y = alt.Y("value:Q", title=y_title)
    base = alt.Chart(data)
    return alt.layer(
        base.mark_tick(thickness=2, size=30, color="black").encode(
            x=x, y=alt.Y("median(value):Q", title=y_title), color=alt.Color("series:N", title=None)
        ),
        base.mark_point(filled=True, size=55, opacity=0.75).encode(
            x=x, y=y, color=alt.Color("series:N", title=None), shape=alt.Shape("series:N", title=None)
        ),
    ).properties(width=400, height=300, title=f"{source} → {target}: embedding distance by condition")


def main():
    report = compare_corpus(codebases_under(DATA, runs_table()))
    rows = report["comparisons"]
    summaries = []
    for source, target in sorted({(r["source_language"], r["target_language"]) for r in rows}):
        selected = [r for r in rows if r["source_language"] == source and r["target_language"] == target]
        pairs = [r for r in selected if r["comparison"] == "port-to-port"]
        refs = [r for r in selected if r["comparison"] == "port-to-reference"]
        within = [r for r in pairs if all(r[f"{f}_a"] == r[f"{f}_b"] for f in
                  ("include_python_tests", "include_typescript_tests"))]
        reference_by_run = {r["run_id_a"]: r["chamfer_distance"] for r in refs}
        summaries.append({
            "direction": f"{source}-to-{target}",
            "port_pair_count": len(pairs), "reference_pair_count": len(refs),
            "port_pair_median": statistics.median(r["chamfer_distance"] for r in pairs),
            "within_condition_pair_count": len(within),
            "within_condition_pair_median": statistics.median(r["chamfer_distance"] for r in within),
            "reference_median": statistics.median(reference_by_run.values()),
            "pairs_closer_than_both_references": sum(
                r["chamfer_distance"] < min(reference_by_run[r["run_id_a"]], reference_by_run[r["run_id_b"]])
                for r in pairs),
        })
        chart = pair_chart(rows, source, target)
        OUT.mkdir(parents=True, exist_ok=True)
        for extension in ("json", "svg", "png"):
            chart.save(OUT / f"port-pairs-{source}-to-{target}.{extension}")
    report["summary"] = summaries
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "port-pair-distances.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
