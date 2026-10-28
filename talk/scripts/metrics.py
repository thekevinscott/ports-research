"""Export cheap V2 model/effort measurements from banked runs.

Run from the worktree root with:
  uv run --project analysis/notebook --locked python talk/scripts/metrics.py \
    --runs-root /home/duncan/work/code/research/ports/experiments/v2-models-effort/runs \
    --output talk/public/models-effort-runs.csv

Reads banked run data; writes only the requested CSV in the worktree.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "analysis" / "notebook"))

from gbnf_experiment.transcript_usage import transcript_usage  # noqa: E402
from src.Codebase import Codebase  # noqa: E402
from src.corpus import EXCLUDE_BY_LANGUAGE  # noqa: E402

MODELS = (
    "claude-fable-5-1",
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "claude-haiku-5-5",
)
EFFORTS = ("low", "medium", "high")
PR_236_MERGED = datetime.fromisoformat("2026-10-25T19:13:00+00:00")
PR_241_MERGED = datetime.fromisoformat("2026-10-27T02:36:00+00:00")
COLUMNS = (
    "run_id",
    "model",
    "effort",
    "direction",
    "wall_minutes",
    "file_count",
    "loc",
    "total_tokens",
)


def minutes(start: str, end: str) -> float:
    created = datetime.fromisoformat(start.replace("Z", "+00:00"))
    ended = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return round((ended - created).total_seconds() / 60, 3)


def setup(created: str) -> str:
    timestamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
    if timestamp < PR_236_MERGED:
        return "before_236"
    if timestamp < PR_241_MERGED:
        return "after_236"
    return "after_241"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    setup_counts = Counter()
    for run_json in sorted(args.runs_root.glob("*/run.json")):
        run = json.loads(run_json.read_text())
        params = run.get("params") or {}
        if (
            run.get("exit_code") != 0
            or run.get("excluded")
            or params.get("model") not in MODELS
            or params.get("effort") not in EFFORTS
            or params.get("source-language") not in ("python", "javascript")
        ):
            continue
        run_dir = run_json.parent
        setup_counts[(params["model"], params["effort"], setup(run["created"]))] += 1
        target = "javascript" if params["source-language"] == "python" else "python"
        port = run_dir / "ported_implementation"
        if not port.is_dir():
            raise FileNotFoundError(f"successful run has no port: {run_dir.name}")
        codebase = Codebase(port, exclude=EXCLUDE_BY_LANGUAGE[target])
        usage = transcript_usage(run_dir)
        rows.append(
            {
                "run_id": run_dir.name,
                "model": params["model"],
                "effort": params["effort"],
                "direction": f"{params['source-language']}→{target}",
                "wall_minutes": minutes(run["created"], run["ended"]),
                "file_count": codebase.file_count,
                "loc": codebase.loc,
                "total_tokens": usage.get("total_tokens", ""),
            }
        )
        if len(rows) % 25 == 0:
            print(f"measured {len(rows)} successful runs", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts_path = args.output.with_name("models-effort-setup-counts.json")
    counts = {
        model: {
            effort: {
                stage: setup_counts[(model, effort, stage)]
                for stage in ("before_236", "after_236", "after_241")
            }
            for effort in EFFORTS
        }
        for model in MODELS
    }
    counts_path.write_text(json.dumps(counts, indent=2) + "\n")
    print(f"wrote {len(rows)} runs to {args.output}", flush=True)
    print(f"wrote setup counts to {counts_path}", flush=True)


if __name__ == "__main__":
    main()
