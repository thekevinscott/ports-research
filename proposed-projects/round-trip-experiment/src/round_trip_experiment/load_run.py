import json
from pathlib import Path

from gbnf_experiment.transcript_usage import transcript_usage


def load_run(run_directory: Path) -> dict:
    manifest = json.loads((run_directory / "manifest.json").read_text())
    result_path = run_directory / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    usage = transcript_usage(run_directory)
    return {
        "run_id": run_directory.name,
        "condition": manifest["condition"],
        "estimate": {
            "total_tokens": usage.get("total_tokens"),
            "api_calls": usage.get("api_calls"),
            "duration_ms": result.get("duration_ms"),
        },
    }
