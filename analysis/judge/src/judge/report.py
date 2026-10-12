import json
from collections import Counter, defaultdict
from pathlib import Path

RUBRICS = Path(__file__).resolve().parents[2] / "rubrics"
FLAGS = (("include_unit_tests", "unit"), ("include_source_integration_tests", "source-int"), ("include_target_integration_tests", "target-int"))


def report(out: Path) -> str:
    """Verdict counts per rubric item by run condition, the baseline items' verdicts, and the unsure items."""

    def labels(verdict) -> list:
        return [str(v) for v in verdict] if isinstance(verdict, list) else [str(verdict)]

    def condition(entry: dict) -> str:
        return " ".join([entry["source_language"], *(f"{short}={int(entry[flag])}" for flag, short in FLAGS)])

    def table(rows: list[list[str]]) -> str:
        widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
        return "\n".join("  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows)

    manifest = json.loads((out / "manifest.json").read_text())
    judgments = [json.loads(line) for line in (out / "judgments.jsonl").read_text().splitlines()]
    unknown = [j["id"] for j in judgments if j["id"] not in manifest]
    if unknown:
        raise ValueError(f"judgments not in the manifest: {', '.join(unknown)}")

    sections, baselines, unsure = [], [], []
    for rubric in sorted({j["rubric"] for j in judgments}):
        properties = json.loads((RUBRICS / f"{rubric}.schema.json").read_text())["properties"]
        judged = [(manifest[j["id"]], j) for j in judgments if j["rubric"] == rubric]
        for name, schema in properties.items():
            verdict = schema["properties"]["verdict"]
            columns = [str(v) for v in verdict.get("enum") or verdict["items"]["enum"]]
            counts, n = defaultdict(Counter), Counter()
            for entry, j in judged:
                if not entry["baseline"]:
                    n[condition(entry)] += 1
                    counts[condition(entry)].update(labels(j["verdicts"][name]["verdict"]))
            rows = [["condition", "n", *columns]] + [[c, str(n[c]), *(str(counts[c][v]) for v in columns)] for c in sorted(n)]
            sections.append(f"{rubric} {name}\n{table(rows)}")
        for entry, j in judged:
            if entry["baseline"]:
                verdicts = " ".join(f"{name}={'+'.join(labels(j['verdicts'][name]['verdict']))}" for name in properties)
                baselines.append(f"baseline {entry['source_language']}->{entry['target_language']} {j['id']}: {verdicts}")
            for name in properties:
                if j["verdicts"][name].get("confidence") == "unsure":
                    unsure.append([j["id"], entry["run"] or "baseline", rubric, f"{name}:", "+".join(labels(j["verdicts"][name]["verdict"]))])

    escalation = table(unsure) if unsure else "none"
    return "\n\n".join([*sections, "\n".join(baselines), f"unsure\n{escalation}"]) + "\n"
