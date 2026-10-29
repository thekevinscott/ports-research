"""Price each banked run from its transcript at Claude API list rates.

  python3 -I scripts/cost_metrics.py --runs-root .../experiments/<experiment>/runs --output public/<experiment>-cost.csv

Every assistant message in the transcript is one API call, priced by its own model and usage.
result.json's total_cost_usd drops calls on some runs; this reads the transcript instead.
Reads banked run data; writes only the requested CSV.
"""

import argparse
import csv
import json
from pathlib import Path

PER_MTOK = {
    "claude-fable-5-1": {"input": 10.0, "output": 50.0, "cache_read": 0.25, "cache_5m": 12.5, "cache_1h": 20.0},
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.20, "cache_5m": 5.0, "cache_1h": 8.0},
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_read": 0.10, "cache_5m": 2.5, "cache_1h": 4.0},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_5m": 0.125, "cache_1h": 0.20},
}
HAIKU_LONG = {"input": 0.50, "output": 2.50, "cache_read": 0.05, "cache_5m": 0.625, "cache_1h": 1.0}
LONG_PROMPT = 100_000

COLUMNS = ("run_id", "model", "effort", "direction", "api_calls", "input_tokens", "cache_write_tokens", "cache_read_tokens", "output_tokens", "transcript_cost_usd", "result_cost_usd", "result_total_tokens", "transcript_total_tokens")


def rates(model: str, usage: dict) -> dict:
    prompt = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
    if model == "claude-haiku-5-5" and prompt > LONG_PROMPT:
        return HAIKU_LONG
    return PER_MTOK[model]


def price(model: str, usage: dict) -> float:
    r = rates(model, usage)
    creation = usage.get("cache_creation") or {}
    write_5m = creation.get("ephemeral_5m_input_tokens", 0)
    write_1h = creation.get("ephemeral_1h_input_tokens", 0)
    if not creation:
        write_5m = usage.get("cache_creation_input_tokens", 0)
    return (
        usage.get("input_tokens", 0) * r["input"]
        + write_5m * r["cache_5m"]
        + write_1h * r["cache_1h"]
        + usage.get("cache_read_input_tokens", 0) * r["cache_read"]
        + usage.get("output_tokens", 0) * r["output"]
    ) / 1_000_000


def transcript_calls(run_dir: Path) -> dict:
    calls = {}
    for path in sorted(run_dir.glob("transcript/**/*.jsonl")):
        for line in path.read_text().splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict) and record.get("type") == "assistant":
                message = record["message"]
                if message.get("model") == "<synthetic>":
                    continue
                calls.setdefault(message["id"], (message.get("model", ""), message["usage"]))
    return calls


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for run_json in sorted(args.runs_root.glob("*/run.json")):
        run = json.loads(run_json.read_text())
        params = run.get("params") or {}
        if run.get("exit_code") != 0 or run.get("excluded") or params.get("source-language") not in ("python", "javascript"):
            continue
        run_dir = run_json.parent
        calls = transcript_calls(run_dir)
        totals = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
        cost = 0.0
        for model, usage in calls.values():
            cost += price(model or params["model"], usage)
            for key in totals:
                totals[key] += usage.get(key, 0)
        result_path = run_dir / "result.json"
        result = json.loads(result_path.read_text()) if result_path.exists() else {}
        result_usage = result.get("usage") or {}
        target = "javascript" if params["source-language"] == "python" else "python"
        rows.append(
            {
                "run_id": run_dir.name,
                "model": params.get("model", ""),
                "effort": params.get("effort", ""),
                "direction": f"{params['source-language']}→{target}",
                "api_calls": len(calls),
                "input_tokens": totals["input_tokens"],
                "cache_write_tokens": totals["cache_creation_input_tokens"],
                "cache_read_tokens": totals["cache_read_input_tokens"],
                "output_tokens": totals["output_tokens"],
                "transcript_cost_usd": round(cost, 4),
                "result_cost_usd": "" if result.get("total_cost_usd") is None else round(result["total_cost_usd"], 4),
                "result_total_tokens": sum(result_usage.get(k, 0) for k in totals) if result_usage else "",
                "transcript_total_tokens": sum(totals.values()),
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
