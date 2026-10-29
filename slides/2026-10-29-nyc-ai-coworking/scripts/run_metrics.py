"""Export per-run measurements for a V2 experiment's banked runs.

Run with the notebook checkout that holds src/Codebase.py and its measure caches:
  uv run --project <notebook> --locked python slides/2026-10-29-nyc-ai-coworking/scripts/run_metrics.py \
    --notebook <notebook> --runs-root /home/duncan/work/code/research/ports/experiments/<experiment>/runs \
    --output slides/2026-10-29-nyc-ai-coworking/public/<experiment>-runs.csv

Reads banked run data; writes only the requested CSV.
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

NOTEBOOK = Path(sys.argv[sys.argv.index("--notebook") + 1]).resolve()
sys.path.insert(0, str(NOTEBOOK))

from gbnf_experiment.transcript_usage import transcript_usage  # noqa: E402
from src.Codebase import Codebase, pinned_reference  # noqa: E402
from src.corpus import EXCLUDE_BY_LANGUAGE, REFERENCE  # noqa: E402

FLAGS = ("include-unit-tests", "include-source-integration-tests", "include-target-integration-tests")
FLAG_NAMES = ("unit", "source", "target")
COLUMNS = (
    "run_id",
    "model",
    "effort",
    "condition",
    "direction",
    "wall_minutes",
    "total_tokens",
    "cost_usd",
    "file_count",
    "loc",
    "diff_lines_changed",
    "reference_diff_similarity_pct",
    "embedding_distance",
    "behavior_agreement_pct",
    "api_agreement_pct",
)


def minutes(start: str, end: str) -> float:
    created = datetime.fromisoformat(start.replace("Z", "+00:00"))
    ended = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return round((ended - created).total_seconds() / 60, 3)


def condition(params: dict) -> str:
    on = [name for flag, name in zip(FLAGS, FLAG_NAMES) if params.get(flag)]
    if not on:
        return "none"
    if len(on) == len(FLAGS):
        return "all"
    return " + ".join(on)


def cost_usd(run_dir: Path) -> float | str:
    """Claude Code's own list-price figure from result.json; empty when the run left none."""
    result = run_dir / "result.json"
    if not result.exists():
        return ""
    cost = json.loads(result.read_text()).get("total_cost_usd")
    return "" if cost is None else round(cost, 4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--notebook", type=Path, required=True, help="analysis/notebook checkout whose src/ and caches to use")
    parser.add_argument("--no-embedding", action="store_true", help="leave embedding_distance empty; it is the one slow, uncached measure")
    parser.add_argument("--no-behavior", action="store_true", help="leave behavior_agreement_pct and api_agreement_pct empty; measure-behavior is minutes per uncached run")
    args = parser.parse_args()
    pinned_reference()
    rows = []
    for run_json in sorted(args.runs_root.glob("*/run.json")):
        run = json.loads(run_json.read_text())
        params = run.get("params") or {}
        if run.get("exit_code") != 0 or run.get("excluded") or params.get("source-language") not in ("python", "javascript"):
            continue
        run_dir = run_json.parent
        target = "javascript" if params["source-language"] == "python" else "python"
        port = run_dir / "ported_implementation"
        if not port.is_dir():
            raise FileNotFoundError(f"successful run has no port: {run_dir.name}")
        if not any(path.is_file() for path in port.rglob("*")):
            print(f"skipped {run_dir.name}: empty port", file=sys.stderr, flush=True)
            continue
        try:
            codebase = Codebase.from_run(
                {"run_dir": str(run_dir), "run_id": run_dir.name, "target_language": target},
                EXCLUDE_BY_LANGUAGE[target],
                reference=REFERENCE / target,
            )
        except (FileNotFoundError, RuntimeError) as error:
            print(f"skipped {run_dir.name}: {error}", file=sys.stderr, flush=True)
            continue
        try:
            usage = transcript_usage(run_dir)
        except AttributeError:
            print(f"no usage for {run_dir.name}: transcript_usage choked on a non-object line", file=sys.stderr, flush=True)
            usage = {}
        diff = codebase._reference_diff
        rows.append(
            {
                "run_id": run_dir.name,
                "model": params.get("model", ""),
                "effort": params.get("effort", ""),
                "condition": condition(params),
                "direction": f"{params['source-language']}→{target}",
                "wall_minutes": minutes(run["created"], run["ended"]),
                "total_tokens": usage.get("total_tokens", ""),
                "cost_usd": cost_usd(run_dir),
                "file_count": codebase.file_count,
                "loc": codebase.loc,
                "diff_lines_changed": diff["insertions"] + diff["deletions"],
                "reference_diff_similarity_pct": round(diff["similarity_pct"], 3),
                "embedding_distance": "" if args.no_embedding else round(codebase.chamfer_distance, 4),
                "behavior_agreement_pct": "" if args.no_behavior else round(codebase.behavior_agreement_pct, 3),
                "api_agreement_pct": "" if args.no_behavior else round(codebase.api_agreement_pct, 3),
            }
        )
        if len(rows) % 25 == 0:
            print(f"measured {len(rows)} successful runs", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} runs to {args.output}", flush=True)


if __name__ == "__main__":
    main()
