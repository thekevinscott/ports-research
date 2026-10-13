"""Judge verdicts joined to their manifest and counted per V2 cell."""

import json
from pathlib import Path

import polars as pl


def load(directory: Path) -> list[dict]:
    """Each judgment's manifest entry with its verdicts."""
    manifest = json.loads((Path(directory) / "manifest.json").read_text())
    judgments = [json.loads(line) for line in (Path(directory) / "judgments.jsonl").read_text().splitlines() if line]
    return [{"id": j["id"], **manifest[j["id"]], "verdicts": j["verdicts"]} for j in judgments]


def questions(schema: Path) -> dict[str, list[str]]:
    """Each rubric question and its fixed verdict values, from the rubric's schema."""
    properties = json.loads(Path(schema).read_text())["properties"]
    return {
        name: [str(v) for v in (spec["properties"]["verdict"].get("enum") or spec["properties"]["verdict"]["items"]["enum"])]
        for name, spec in properties.items()
    }


def split(items: list[dict], run_ids: set[str]) -> tuple[list[dict], list[dict], list[dict]]:
    """Items on a notebook run, baseline items, and items on any other run."""
    runs = [i for i in items if not i["baseline"] and i["run"] in run_ids]
    baselines = [i for i in items if i["baseline"]]
    unmatched = [i for i in items if not i["baseline"] and i["run"] not in run_ids]
    return runs, baselines, unmatched


def labels(verdict) -> list[str]:
    return [str(v) for v in verdict] if isinstance(verdict, list) else [str(verdict)]


def condition(item: dict, conditions, flags) -> str | None:
    for label, *values in conditions:
        if all(bool(item[flag]) == value for flag, value in zip(flags, values)):
            return label
    return None


def verdict_counts(items, question, values, conditions, flags, sources) -> pl.DataFrame:
    """Per source language and condition, n items and how many carry each verdict value."""
    values = [str(v) for v in values]
    rows = []
    for source in sources:
        for label, *_ in conditions:
            cell = [i for i in items if i["source_language"] == source and condition(i, conditions, flags) == label]
            given = [v for i in cell for v in labels(i["verdicts"][question]["verdict"])]
            rows.append({"source_language": source, "condition": label, "n": len(cell), **{v: given.count(v) for v in values}})
    return pl.DataFrame(rows, schema={"source_language": pl.String, "condition": pl.String, "n": pl.Int64, **{v: pl.Int64 for v in values}})


def fidelity_runs(items, conditions, flags) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "run_id": i["run"],
                "source_language": i["source_language"],
                "target_language": i["target_language"],
                "condition": condition(i, conditions, flags),
                "fidelity": int(i["verdicts"]["fidelity"]["verdict"]),
            }
            for i in items
        ],
        schema={"run_id": pl.String, "source_language": pl.String, "target_language": pl.String, "condition": pl.String, "fidelity": pl.Int64},
    )


def per_run(items, names, conditions, flags) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "run_id": i["run"],
                "item": i["id"],
                "source_language": i["source_language"],
                "condition": condition(i, conditions, flags),
                **{name: "+".join(labels(i["verdicts"][name]["verdict"])) for name in names},
            }
            for i in items
        ],
        schema={"run_id": pl.String, "item": pl.String, "source_language": pl.String, "condition": pl.String, **{n: pl.String for n in names}},
    )


def baseline_rows(items, names) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "baseline": f"human {i['source_language']} (A) vs human {i['target_language']} (B)",
                "item": i["id"],
                **{name: "+".join(labels(i["verdicts"][name]["verdict"])) for name in names},
            }
            for i in items
        ],
        schema={"baseline": pl.String, "item": pl.String, **{n: pl.String for n in names}},
    )


def unsure(items, names) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "run_id": i["run"],
                "item": i["id"],
                "source_language": i["source_language"],
                "question": name,
                "verdict": "+".join(labels(i["verdicts"][name]["verdict"])),
            }
            for i in items
            for name in names
            if i["verdicts"][name].get("confidence") == "unsure"
        ],
        schema={"run_id": pl.String, "item": pl.String, "source_language": pl.String, "question": pl.String, "verdict": pl.String},
    )
