"""Median diff lines between ports within each model × effort cell, and against the reference.

  uv run --project <notebook> --locked python slides/2026-10-29-nyc-ai-coworking/scripts/pair_metrics.py \
    --notebook <notebook> --runs-root experiments/v2-models-effort/runs --output public/models-effort-pairs.json
"""

import argparse
import json
import statistics
import sys
from itertools import combinations
from pathlib import Path

NOTEBOOK = Path(sys.argv[sys.argv.index("--notebook") + 1]).resolve()
sys.path.insert(0, str(NOTEBOOK))

from src.Codebase import exclude_args, pinned_reference, run_git_diff  # noqa: E402
from src.corpus import EXCLUDE_BY_LANGUAGE, REFERENCE  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from run_metrics import condition  # noqa: E402

EFFORTS = ["low", "medium", "high", "xhigh"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--notebook", type=Path, required=True)
    parser.add_argument("--by", choices=["model-effort", "condition"], default="model-effort")
    args = parser.parse_args()
    pinned_reference()
    cells: dict[tuple, list[Path]] = {}
    for run_json in sorted(args.runs_root.glob("*/run.json")):
        run = json.loads(run_json.read_text())
        params = run.get("params") or {}
        if run.get("exit_code") != 0 or run.get("excluded"):
            continue
        if args.by == "model-effort" and params.get("effort") not in EFFORTS:
            continue
        target = "javascript" if params["source-language"] == "python" else "python"
        if not any(path.is_file() for path in (run_json.parent / "ported_implementation").rglob("*")):
            print(f"skipped {run_json.parent.name}: empty port", file=sys.stderr, flush=True)
            continue
        cell = (params["model"], params["effort"]) if args.by == "model-effort" else ("claude-opus-5-5", condition(params))
        cells.setdefault((f"{params['source-language']}→{target}", *cell), []).append(
            run_json.parent / "ported_implementation"
        )
    rows = []
    for (direction, model, effort), ports in sorted(cells.items()):
        key = "effort" if args.by == "model-effort" else "condition"
        target = direction.split("→")[1]
        exclude = exclude_args(EXCLUDE_BY_LANGUAGE[target])
        pairs = [
            run_git_diff(a, b, language=target, exclude=exclude) for a, b in combinations(ports, 2)
        ]
        refs = [run_git_diff(REFERENCE / target, port, language=target, exclude=exclude) for port in ports]
        lines = lambda d: d["insertions"] + d["deletions"]  # noqa: E731
        rows.append(
            {
                "direction": direction,
                "model": model,
                key: effort,
                "ports": len(ports),
                "pair_lines_median": round(statistics.median(lines(d) for d in pairs)),
                "pair_pct_median": round(statistics.median(d["similarity_pct"] for d in pairs), 1),
                "pairs": len(pairs),
                "reference_lines_median": round(statistics.median(lines(d) for d in refs)),
                "reference_pct_median": round(statistics.median(d["similarity_pct"] for d in refs), 1),
            }
        )
        print(f"{direction} {model} {effort}: {len(ports)} ports, {len(pairs)} pairs", flush=True)
        args.output.write_text(json.dumps(rows, indent=1) + "\n")
    print(f"wrote {len(rows)} cells to {args.output}", flush=True)


if __name__ == "__main__":
    main()
