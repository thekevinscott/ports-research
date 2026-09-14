import json
import subprocess
import uuid
from pathlib import Path


def hyperfine_mean(*, command: str, scratch: Path) -> float:
    """Mean wall-clock seconds for one shell command, from a real hyperfine run.

    Shared by both language drivers so a baseline (fixed-overhead) measurement
    and a real-work measurement go through the exact same timing methodology.
    """
    report_path = scratch / f"{uuid.uuid4().hex}.json"
    process = subprocess.run(
        ["hyperfine", "--warmup", "1", "--min-runs", "3", "--export-json", str(report_path), command],
        capture_output=True,
        text=True,
    )
    if not report_path.is_file():
        raise RuntimeError(f"hyperfine produced no report (exit {process.returncode}): {process.stderr}")
    return json.loads(report_path.read_text())["results"][0]["mean"]
