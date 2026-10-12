import json
from datetime import datetime
from pathlib import Path


def transcript_wall_ms(run_directory: Path) -> int | None:
    """First to last timestamp across every session file of the run, subagents included."""
    stamps = []
    for path in run_directory.glob("transcript/**/*.jsonl"):
        for line in path.read_text().splitlines():
            try:
                timestamp = json.loads(line).get("timestamp")
            except (ValueError, AttributeError):
                continue
            if timestamp:
                stamps.append(datetime.fromisoformat(timestamp))
    if not stamps:
        return None
    return round((max(stamps) - min(stamps)).total_seconds() * 1000)
