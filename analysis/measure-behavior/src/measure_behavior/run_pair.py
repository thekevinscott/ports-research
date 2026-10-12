import json
import os
import signal
import subprocess
import sys
from pathlib import Path

DRIVERS = Path(__file__).resolve().parents[2] / "drivers"
TIMEOUT_SECONDS = 10
TSX = "tsx@4.19.2"


def run_pair(language: str, implementation: Path, grammar: str, text: str) -> dict:
    if language == "python":
        command = [sys.executable, str(DRIVERS / "driver.py")]
        env = {**os.environ, "PYTHONPATH": str(implementation), "PYTHONDONTWRITEBYTECODE": "1"}
    else:
        command = ["pnpm", "--silent", "dlx", TSX, str(DRIVERS / "driver.mts"), str(implementation / "src" / "index.ts")]
        env = dict(os.environ)
    # Its own session, so a timeout kills pnpm's node child along with pnpm.
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(json.dumps({"grammar": grammar, "input": text}), timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return {"outcome": "crash", "error": f"timed out after {TIMEOUT_SECONDS}s"}
    if process.returncode != 0 or not stdout.strip():
        return {"outcome": "crash", "error": stderr.strip() or f"exit {process.returncode} with no outcome"}
    return json.loads(stdout)
