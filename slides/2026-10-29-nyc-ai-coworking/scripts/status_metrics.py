"""Per-run behaviour driver status for v2-models-effort, from the notebook's warm measure caches.

  uv run --project <notebook> --locked python slides/2026-10-29-nyc-ai-coworking/scripts/status_metrics.py \
    --notebook <notebook> --runs-root .../experiments/v2-models-effort/runs \
    --output slides/2026-10-29-nyc-ai-coworking/public/models-effort-status.csv

Status rule copied from the notebook's behavior_driver_status: not_loaded when every pair crashed,
loaded_failing when the port accepts none of the inputs the reference accepts, driven otherwise.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

NOTEBOOK = Path(sys.argv[sys.argv.index("--notebook") + 1]).resolve()
sys.path.insert(0, str(NOTEBOOK))

from src.Codebase import Codebase, pinned_reference  # noqa: E402
from src.corpus import EXCLUDE_BY_LANGUAGE, REFERENCE  # noqa: E402

COLUMNS = ("run_id", "model", "effort", "direction", "status", "agreements", "pairs", "confusion", "error")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--notebook", type=Path, required=True)
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
        if not port.is_dir() or not any(path.is_file() for path in port.rglob("*")):
            continue
        try:
            codebase = Codebase.from_run(
                {"run_dir": str(run_dir), "run_id": run_dir.name, "target_language": target},
                EXCLUDE_BY_LANGUAGE[target],
                reference=REFERENCE / target,
            )
            behavior = codebase._behavior
        except (FileNotFoundError, RuntimeError) as error:
            print(f"skipped {run_dir.name}: {error}", file=sys.stderr, flush=True)
            continue
        confusion = behavior["confusion"]
        pairs = sum(sum(v.values()) for v in confusion.values())
        crashes = sum(v.get("crash", 0) for v in confusion.values())
        accepted = confusion.get("accept", {}).get("accept", 0)
        status = "not_loaded" if crashes == pairs else "loaded_failing" if accepted == 0 else "driven"
        note = behavior.get("note") or ""
        errors = re.findall(r"^(\w+(?:Error|Exception)[^\n]{0,80})", note, re.M)
        rows.append(
            {
                "run_id": run_dir.name,
                "model": params.get("model", ""),
                "effort": params.get("effort", ""),
                "direction": f"{params['source-language']}→{target}",
                "status": status,
                "agreements": behavior["agreements"],
                "pairs": behavior["pairs"],
                "confusion": json.dumps({f"{a}>{b}": n for a, v in confusion.items() for b, n in v.items() if n}, sort_keys=True),
                "error": (errors[-1] if errors else note.replace("every pair crashed: ", "")[:80]).replace("\n", " "),
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} runs to {args.output}", flush=True)


if __name__ == "__main__":
    main()
