"""Join cached ladder pickles onto a runs CSV: ladder_ref_ratio, ladder_rungs_completed, ladder_total_ms per run.

Formulas copied from notebook-v1 analysis/notebook/src/Codebase.py (ladder_ref_ratio,
ladder_rungs_completed, ladder_total_ms). A run with no pickle or a LoadError pickle gets empty cells.

    uv run --script scripts/ladder_metrics.py public/tests-configuration-runs.csv public/tests-configuration-ladder.csv
"""

import csv
import pickle
import statistics
import sys
from pathlib import Path

LADDER = Path.home() / ".cache" / "ports" / "analysis" / "codebases" / "exercise-api" / "ladder"
KEEP = ["run_id", "model", "effort", "condition", "direction"]


def add_ms(entry: dict) -> float:
    return entry["add_ns"]["median"] / 1e6


def metrics(run_id: str) -> dict[str, str]:
    path = LADDER / f"{run_id}.pkl"
    if not path.exists():
        return {}
    result = pickle.loads(path.read_bytes())
    timings = result.get("timings")
    reference = result.get("reference_timings")
    if not timings:
        return {}
    target_median = statistics.median(add_ms(e) for e in timings)
    reference_median = statistics.median(add_ms(e) for e in reference) if reference else None
    return {
        "ladder_ref_ratio": f"{target_median / reference_median:.4f}" if reference_median else "",
        "ladder_rungs_completed": str(len(timings)),
        "ladder_total_ms": f"{sum(add_ms(e) for e in timings):.1f}",
    }


def main(source: str, output: str) -> None:
    rows = list(csv.DictReader(open(source)))
    fields = [k for k in KEEP if k in rows[0]] + ["ladder_ref_ratio", "ladder_rungs_completed", "ladder_total_ms"]
    with open(output, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {k: row[k] for k in fields if k in row}
            out.update(metrics(row["run_id"]))
            writer.writerow(out)
    timed = sum(1 for r in csv.DictReader(open(output)) if r["ladder_ref_ratio"])
    print(f"{output}: {len(rows)} runs, {timed} with ladder timings")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
