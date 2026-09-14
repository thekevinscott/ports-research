import json
from pathlib import Path


def transcript_usage(run_directory: Path) -> dict:
    calls = {}
    for path in sorted(run_directory.glob("transcript/**/*.jsonl")):
        for line in path.read_text().splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get("type") == "assistant":
                calls.setdefault(record["message"]["id"], record["message"]["usage"])
    if not calls:
        return {}
    return {
        "total_tokens": sum(
            u["input_tokens"]
            + u["cache_creation_input_tokens"]
            + u["cache_read_input_tokens"]
            + u["output_tokens"]
            for u in calls.values()
        ),
        "api_calls": len(calls),
    }
